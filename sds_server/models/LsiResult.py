class LsiResult:
    def __init__(self, id, similarity):
        self.id = id
        self.similarity = similarity

    def to_dict(self):
        return {'id': self.id, 'similarity': self.similarity}
