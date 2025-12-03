#!/usr/bin/env python3

import logging
import sys
from contextlib import contextmanager

import Ice
from Ice import identityToString as id2str

from gst_player import GstPlayer

Ice.loadSlice('-I{} spotifice_v1.ice'.format(Ice.getSliceDir()))
import Spotifice  # type: ignore # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MediaRender")


class MediaRenderI(Spotifice.MediaRender):
    def __init__(self, player):
        self.player = player
        self.server: Spotifice.MediaServerPrx = None
        self.current_track = None
        # Nuevo en Hito 1: Gestión de playlists y estado de reproducción
        self.current_playlist = None  # Objeto Playlist
        self.playlist_position = -1   # Posición actual en la playlist
        self.playback_history = []    # Historial de track_ids reproducidos
        self.repeat_mode = False      # Modo repeat activado/desactivado
        self.playback_state = Spotifice.PlaybackState.STOPPED  # Estado actual
        self.proxy_actual = None      # Guarda el proxy actual para el hook de pista agotada

    def ensure_player_stopped(self):
        if self.player.is_playing():
            raise Spotifice.PlayerError(reason="Already playing")

    def ensure_server_bound(self):
        if not self.server:
            raise Spotifice.BadReference(reason="No MediaServer bound")

    # --- RenderConnectivity ---

    def bind_media_server(self, media_server, current=None):
        try:
            proxy = media_server.ice_timeout(500)
            proxy.ice_ping()
        except Ice.ConnectionRefusedException as e:
            raise Spotifice.BadReference(reason=f"MediaServer not reachable: {e}")

        self.server = media_server
        # Resetear historial cuando se enlaza nuevo servidor
        self.playback_history = []
        logger.info(f"Bound to MediaServer '{id2str(media_server.ice_getIdentity())}'")

    def unbind_media_server(self, current=None):
        self.stop(current)
        self.server = None
        self.current_playlist = None
        self.playlist_position = -1
        self.playback_history = []
        logger.info("Unbound MediaServer")

    # --- ContentManager ---

    def load_track(self, track_id, current=None):
        self.ensure_server_bound()

        try:
            # Cargar track individual cancela el contexto de playlist
            self.current_playlist = None
            self.playlist_position = -1
            
            with self.keep_playing_state(current):
                self.current_track = self.server.get_track_info(track_id)

            logger.info(f"Current track set to: {self.current_track.title}")

        except Spotifice.TrackError as e:
            logger.error(f"Error setting track: {e.reason}")
            raise

    def get_current_track(self, current=None):
        return self.current_track

    def load_playlist(self, playlist_id, current=None):
        # Cargar playlist y establecer primera pista sin reproducir
        self.ensure_server_bound()

        try:
            # Obtener playlist desde el servidor
            self.current_playlist = self.server.get_playlist(playlist_id)
            
            # Resetear historial al cargar nueva playlist
            self.playback_history = []
            
            # Verificar que la playlist tiene pistas
            if not self.current_playlist.track_ids:
                raise Spotifice.PlaylistError(reason="Playlist is empty")
            
            # Establecer posición en la primera pista
            self.playlist_position = 0
            primera_pista_id = self.current_playlist.track_ids[0]
            
            # Cargar primera pista pero NO reproducir
            self.current_track = self.server.get_track_info(primera_pista_id)
            
            # Añadir primera pista al historial para que previous() funcione después de next()
            self.playback_history.append(self.current_track.id)
            
            logger.info(f"Loaded playlist '{self.current_playlist.name}' "
                       f"with {len(self.current_playlist.track_ids)} tracks. "
                       f"First track: {self.current_track.title}")
            
        except Spotifice.PlaylistError as e:
            logger.error(f"Error loading playlist: {e.reason}")
            raise
        except Spotifice.TrackError as e:
            logger.error(f"Error loading first track: {e.reason}")
            raise

    # --- PlaybackController ---

    @contextmanager
    def keep_playing_state(self, current):
        playing = self.player.is_playing()
        if playing:
            self.stop(current)
        try:
            yield
        finally:
            if playing:
                self.play(current)

    def handle_track_exhausted(self):
        # Handler llamado automáticamente cuando una pista termina
        # Implementa la lógica completa de repeat según el contexto
        logger.info("Track exhausted, handling repeat logic...")
        
        if self.current_playlist:
            # Tenemos playlist cargada
            if self.playlist_position < len(self.current_playlist.track_ids) - 1:
                # No es la última pista, avanzar automáticamente
                try:
                    self.playlist_position += 1
                    id_pista = self.current_playlist.track_ids[self.playlist_position]
                    self.current_track = self.server.get_track_info(id_pista)
                    logger.info(f"Auto-advancing to next track: {self.current_track.title}")
                    self.play(self.proxy_actual)
                except Exception as e:
                    logger.error(f"Error auto-advancing to next track: {e}")
                    self.playback_state = Spotifice.PlaybackState.STOPPED
            else:
                # Es la última pista de la playlist
                if self.repeat_mode:
                    # Repetir playlist desde el inicio
                    logger.info("End of playlist reached, restarting (repeat mode)")
                    self.playlist_position = 0
                    try:
                        id_pista = self.current_playlist.track_ids[0]
                        self.current_track = self.server.get_track_info(id_pista)
                        self.play(self.proxy_actual)
                    except Exception as e:
                        logger.error(f"Error restarting playlist: {e}")
                        self.playback_state = Spotifice.PlaybackState.STOPPED
                else:
                    # Fin de playlist sin repeat, parar
                    logger.info("End of playlist reached, stopping")
                    self.playback_state = Spotifice.PlaybackState.STOPPED
        else:
            # Pista individual (sin playlist)
            if self.repeat_mode:
                # Repetir la misma pista
                logger.info("Track finished, repeating (repeat mode)")
                try:
                    self.play(self.proxy_actual)
                except Exception as e:
                    logger.error(f"Error repeating track: {e}")
                    self.playback_state = Spotifice.PlaybackState.STOPPED
            else:
                # Fin de pista sin repeat, parar
                logger.info("Track finished, stopping")
                self.playback_state = Spotifice.PlaybackState.STOPPED

    def play(self, current=None):
        def get_chunk_hook(chunk_size):
            try:
                return self.server.get_audio_chunk(current.id, chunk_size)
            except Spotifice.IOError as e:
                logger.error(e)
            except Ice.Exception as e:
                logger.critical(e)

        assert current, "remote invocation required"

        # Si estamos en pausa, simplemente reanudar
        if self.playback_state == Spotifice.PlaybackState.PAUSED:
            self.player.resume()
            self.playback_state = Spotifice.PlaybackState.PLAYING
            logger.info("Resumed from pause")
            return

        self.ensure_player_stopped()
        self.ensure_server_bound()

        if not self.current_track:
            raise Spotifice.TrackError(reason="No track loaded")

        # Guardar proxy para usar en el hook de pista agotada
        self.proxy_actual = current

        try:
            self.server.open_stream(self.current_track.id, current.id)
        except Spotifice.BadIdentity as e:
            logger.error(f"Error starting stream: {e.reason}")
            raise Spotifice.StreamError(reason="Strean setup failed")

        # Configurar player con hook de fin de pista
        self.player.configure(get_chunk_hook, track_exhausted_hook=self.handle_track_exhausted)
        if not self.player.confirm_play_starts():
            raise Spotifice.PlayerError(reason="Failed to confirm playback")
        
        # Actualizar estado e historial
        self.playback_state = Spotifice.PlaybackState.PLAYING
        if self.current_track.id not in self.playback_history:
            self.playback_history.append(self.current_track.id)

    def stop(self, current=None):
        if self.server and current:
            self.server.close_stream(current.id)

        if not self.player.stop():
            raise Spotifice.PlayerError(reason="Failed to confirm stop")

        # Actualizar estado: stop reinicia al inicio pero mantiene posición de playlist
        self.playback_state = Spotifice.PlaybackState.STOPPED
        logger.info("Stopped")

    def pause(self, current=None):
        # Pausar reproducción
        if not self.player.is_playing():
            raise Spotifice.PlayerError(reason="Not currently playing")
        
        try:
            self.player.pause()
            self.playback_state = Spotifice.PlaybackState.PAUSED
            logger.info("Paused")
        except Exception as e:
            raise Spotifice.PlayerError(reason=f"Failed to pause: {e}")

    def get_status(self, current=None):
        # Devolver estado actual de reproducción
        status = Spotifice.PlaybackStatus()
        status.state = self.playback_state
        status.current_track_id = self.current_track.id if self.current_track else ""
        status.repeat = self.repeat_mode
        return status

    def next(self, current=None):
        # Avanzar a siguiente pista en playlist, manteniendo estado play/pause
        if not self.current_playlist:
            raise Spotifice.PlaylistError(reason="No playlist loaded")
        
        # Recordar estado actual
        estaba_reproduciendo = (self.playback_state == Spotifice.PlaybackState.PLAYING)
        
        # Detener reproducción actual si está reproduciendo
        if estaba_reproduciendo:
            self.stop(current)
        
        # Avanzar a siguiente pista
        self.playlist_position += 1
        
        # Verificar si alcanzamos el final
        if self.playlist_position >= len(self.current_playlist.track_ids):
            if self.repeat_mode:
                # Reiniciar desde el inicio
                self.playlist_position = 0
                logger.info("Reached end of playlist, restarting (repeat mode)")
            else:
                # Quedarse en última pista sin lanzar error
                self.playlist_position = len(self.current_playlist.track_ids) - 1
                logger.info("Already at end of playlist, staying at last track")
                # No hacer nada más, mantener el estado actual
                return
        
        # Cargar la nueva pista
        id_pista = self.current_playlist.track_ids[self.playlist_position]
        self.current_track = self.server.get_track_info(id_pista)
        logger.info(f"Next track: {self.current_track.title}")
        
        # Añadir al historial para que previous() funcione
        if self.current_track.id not in self.playback_history:
            self.playback_history.append(self.current_track.id)
        
        # Reanudar reproducción si estaba reproduciendo
        if estaba_reproduciendo:
            self.play(current)

    def previous(self, current=None):
        # Retroceder a pista anterior en historial, manteniendo estado play/pause
        if len(self.playback_history) < 2:
            raise Spotifice.PlaylistError(reason="No previous track in history")
        
        # Recordar estado actual
        estaba_reproduciendo = (self.playback_state == Spotifice.PlaybackState.PLAYING)
        
        # Detener reproducción actual si está reproduciendo
        if estaba_reproduciendo:
            self.stop(current)
        
        # Eliminar pista actual del historial
        self.playback_history.pop()
        
        # Obtener pista anterior
        id_pista_anterior = self.playback_history[-1]
        
        # Actualizar posición de playlist si estamos en una playlist
        if self.current_playlist:
            try:
                self.playlist_position = self.current_playlist.track_ids.index(id_pista_anterior)
            except ValueError:
                # Pista no está en la playlist actual (de diferente playlist/servidor)
                self.playlist_position = -1
        
        # Cargar la pista anterior
        self.current_track = self.server.get_track_info(id_pista_anterior)
        logger.info(f"Previous track: {self.current_track.title}")
        
        # Reanudar reproducción si estaba reproduciendo
        if estaba_reproduciendo:
            self.play(current)

    def set_repeat(self, value, current=None):
        # Establecer modo repeat
        self.repeat_mode = value
        logger.info(f"Repeat mode: {'ON' if value else 'OFF'}")


def main(ic, player):
    servant = MediaRenderI(player)

    adapter = ic.createObjectAdapter("MediaRenderAdapter")
    proxy = adapter.add(servant, ic.stringToIdentity("mediaRender1"))
    logger.info(f"MediaRender: {proxy}")

    adapter.activate()
    ic.waitForShutdown()

    logger.info("Shutdown")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: media_render.py <config-file>")

    player = GstPlayer()
    player.start()
    try:
        with Ice.initialize(sys.argv) as communicator:
            main(communicator, player)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user.")
    finally:
        player.shutdown()
