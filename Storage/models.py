from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func, BigInteger, Float, Boolean
class Base(DeclarativeBase):
    pass
# class MatchReport(Base):
#     __tablename__ = "match_report"
#     match_id = mapped_column(String(50), primary_key=True)
#     rank = mapped_column(String(50), nullable=False)
#     winner = mapped_column(Boolean, nullable=False)
#     timestamp = mapped_column(DateTime, nullable=False, default=func.now())
#     duration = mapped_column(Float, nullable=False)
#     trace_id = mapped_column(String(50), nullable=False)
    

# class DisconnectionReport(Base):
#     __tablename__ = "disconnection_report"
#     disconnection_id = mapped_column(String, primary_key=True)
#     region = mapped_column(String(50), nullable=False)
#     server = mapped_column(String(50), nullable=False)
#     timestamp = mapped_column(DateTime, nullable=False, default=func.now())
#     duration = mapped_column(Float, nullable=False)
#     latency = mapped_column(Integer, nullable=False)
#     trace_id = mapped_column(String(50), nullable=False)

class MatchReport(Base):
    __tablename__ = "match_report"
    match_id = mapped_column(String(50), primary_key=True)
    rank = mapped_column(String(50), nullable=False)
    winner = mapped_column(Boolean, nullable=False)
    timestamp = mapped_column(DateTime, nullable=False, default=func.now())
    duration = mapped_column(Float, nullable=False)
    trace_id = mapped_column(String(50), nullable=False)

    def to_dict(self):
        return {
            'match_id': self.match_id,
            'rank': self.rank,
            'winner': self.winner,
            'timestamp': self.timestamp,
            'duration': self.duration,
            'trace_id': self.trace_id
        }


class DisconnectionReport(Base):
    __tablename__ = "disconnection_report"
    disconnection_id = mapped_column(String, primary_key=True)
    region = mapped_column(String(50), nullable=False)
    server = mapped_column(String(50), nullable=False)
    timestamp = mapped_column(DateTime, nullable=False, default=func.now())
    duration = mapped_column(Float, nullable=False)
    latency = mapped_column(Integer, nullable=False)
    trace_id = mapped_column(String(50), nullable=False)

    def to_dict(self):
        return {
            'disconnection_id': self.disconnection_id,
            'region': self.region,
            'server': self.server,
            'timestamp': self.timestamp,
            'duration': self.duration,
            'latency': self.latency,
            'trace_id': self.trace_id
        }
