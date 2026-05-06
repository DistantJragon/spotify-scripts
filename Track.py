class Track:
    def __init__(self, track_name, artist_name, track_index, track_id):
        self.track_name = track_name
        self.artist_name = artist_name
        self.track_index = track_index
        self.track_id = track_id
        self.audio_features = None
       
    def set_audio_features(self, audio_features):
        self.audio_features = audio_features

    def to_dict(self):
        track_json = {
            "track_name": self.track_name,
            "artist_name": self.artist_name,
            "track_index": self.track_index,
            "track_id": self.track_id,
            "audio_features": self.audio_features
        }
        return track_json
