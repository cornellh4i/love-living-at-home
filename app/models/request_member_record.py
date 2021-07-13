from .. import db


class RequestMemberRecord(db.Model):
    """
    A record of a member who has requested a request. 
    """
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer,
                           db.ForeignKey('request.id'),
                           nullable=False)
    member_id = db.Column(db.Integer,
                          db.ForeignKey('member.id'),
                          nullable=False)

    def __repr__(self):
        return f"RequestMemberRecord('Request ID: {self.request_id}, Member ID: {self.member_id}')"
