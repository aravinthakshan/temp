# connection.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Text, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date, datetime
import random
import string

# Create SQLAlchemy engine
ENGINE_URL = 'mysql+mysqlconnector://root:avi-123+@localhost/fastlink'
engine = create_engine(ENGINE_URL)

# Create base class for models
Base = declarative_base()

# Create session factory
Session = sessionmaker(bind=engine)

# Define models
class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)
    
    bookings = relationship("Booking", back_populates="user")

class Station(Base):
    __tablename__ = 'stations'
    
    station_id = Column(Integer, primary_key=True)
    station_name = Column(String(100), nullable=False)
    
    source_trains = relationship("Train", foreign_keys="Train.source_id", back_populates="source_station")
    destination_trains = relationship("Train", foreign_keys="Train.destination_id", back_populates="destination_station")

class Train(Base):
    __tablename__ = 'trains'
    
    train_id = Column(Integer, primary_key=True)
    train_number = Column(String(20), unique=True, nullable=False)
    train_name = Column(String(100), nullable=False)
    source_id = Column(Integer, ForeignKey('stations.station_id'), nullable=False)
    destination_id = Column(Integer, ForeignKey('stations.station_id'), nullable=False)
    departure_time = Column(String(20), nullable=False)
    arrival_time = Column(String(20), nullable=False)
    travel_days = Column(String(100), nullable=False)
    
    source_station = relationship("Station", foreign_keys=[source_id], back_populates="source_trains")
    destination_station = relationship("Station", foreign_keys=[destination_id], back_populates="destination_trains")
    bookings = relationship("Booking", back_populates="train")

class Booking(Base):
    __tablename__ = 'bookings'
    
    booking_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    train_id = Column(Integer, ForeignKey('trains.train_id'), nullable=False)
    pnr_number = Column(String(10), unique=True, nullable=False)
    booking_date = Column(Date, nullable=False)
    travel_date = Column(Date, nullable=False)
    status = Column(String(20), default='Confirmed', nullable=False)
    
    user = relationship("User", back_populates="bookings")
    train = relationship("Train", back_populates="bookings")
    tickets = relationship("Ticket", back_populates="booking")
    cancellation = relationship("Cancellation", uselist=False, back_populates="booking")

class Ticket(Base):
    __tablename__ = 'tickets'
    
    ticket_id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.booking_id'), nullable=False)
    passenger_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    
    booking = relationship("Booking", back_populates="tickets")

class Cancellation(Base):
    __tablename__ = 'cancellations'
    
    cancellation_id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.booking_id'), unique=True, nullable=False)
    cancelled_on = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    
    booking = relationship("Booking", back_populates="cancellation")

# Create tables if they don't exist
Base.metadata.create_all(engine)

# ------------------ HELPER FUNCTIONS ------------------

def generate_pnr():
    """Generate a random 10-character PNR number."""
    return ''.join(random.choices(string.digits, k=10))

# ------------------ USER AUTHENTICATION ------------------

def login_user(username, password):
    """Authenticate a user by username and password."""
    session = Session()
    try:
        user = session.query(User).filter_by(username=username, password=password, is_admin=False).first()
        if user:
            return {
                'user_id': user.user_id,
                'username': user.username
            }
        return None
    finally:
        session.close()

def login_admin(username, password):
    """Authenticate an admin user by username and password."""
    session = Session()
    try:
        admin = session.query(User).filter_by(username=username, password=password, is_admin=True).first()
        if admin:
            return {
                'user_id': admin.user_id,
                'username': admin.username
            }
        return None
    finally:
        session.close()

def register_user(username, password):
    """Register a new user."""
    session = Session()
    try:
        # Check if username already exists
        if session.query(User).filter_by(username=username).first():
            raise ValueError("Username already exists")
        
        new_user = User(username=username, password=password, is_admin=False)
        session.add(new_user)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# ------------------ TRAIN SEARCH ------------------

def search_train_by_number(train_number):
    """Search for trains by train number."""
    session = Session()
    try:
        train = session.query(Train).filter_by(train_number=train_number).first()
        if not train:
            return []
            
        source_station = session.query(Station).filter_by(station_id=train.source_id).first()
        destination_station = session.query(Station).filter_by(station_id=train.destination_id).first()
        
        result = {
            'train_id': train.train_id,
            'train_number': train.train_number,
            'train_name': train.train_name,
            'departure_time': train.departure_time,
            'arrival_time': train.arrival_time,
            'travel_days': train.travel_days,
            'source': source_station.station_name if source_station else "Unknown",
            'destination': destination_station.station_name if destination_station else "Unknown"
        }
        
        return [result]
    finally:
        session.close()

def search_train_by_location(source, destination):
    """Search for trains by source and destination stations."""
    session = Session()
    try:
        # Find the station IDs
        source_station = session.query(Station).filter_by(station_name=source).first()
        destination_station = session.query(Station).filter_by(station_name=destination).first()
        
        if not source_station or not destination_station:
            return []
            
        # Search for trains with these source and destination
        trains = session.query(Train).filter_by(
            source_id=source_station.station_id,
            destination_id=destination_station.station_id
        ).all()
        
        results = []
        for train in trains:
            results.append({
                'train_id': train.train_id,
                'train_number': train.train_number,
                'train_name': train.train_name,
                'departure_time': train.departure_time,
                'arrival_time': train.arrival_time,
                'travel_days': train.travel_days,
                'source': source,
                'destination': destination
            })
            
        return results
    finally:
        session.close()

def get_all_trains():
    """Get a list of all trains with source and destination names."""
    session = Session()
    try:
        trains = session.query(Train).all()
        results = []
        
        for train in trains:
            source_station = session.query(Station).filter_by(station_id=train.source_id).first()
            destination_station = session.query(Station).filter_by(station_id=train.destination_id).first()
            
            results.append({
                'train_id': train.train_id,
                'train_number': train.train_number,
                'train_name': train.train_name,
                'departure_time': train.departure_time,
                'arrival_time': train.arrival_time,
                'travel_days': train.travel_days,
                'source': source_station.station_name if source_station else "Unknown",
                'destination': destination_station.station_name if destination_station else "Unknown"
            })
            
        return results
    finally:
        session.close()

# ------------------ BOOKING ------------------

def book_ticket(user_id, train_id, travel_date, booking_date, passenger_list):
    """Book tickets for multiple passengers."""
    session = Session()
    try:
        # Generate a unique PNR
        pnr = generate_pnr()
        
        # Create booking
        new_booking = Booking(
            user_id=user_id,
            train_id=train_id,
            pnr_number=pnr,
            booking_date=booking_date,
            travel_date=travel_date,
            status='Confirmed'
        )
        session.add(new_booking)
        session.flush()  # To get the booking_id
        
        # Create tickets for each passenger
        for passenger in passenger_list:
            new_ticket = Ticket(
                booking_id=new_booking.booking_id,
                passenger_name=passenger['name'],
                age=passenger['age'],
                gender=passenger['gender']
            )
            session.add(new_ticket)
        
        session.commit()
        return new_booking.booking_id, pnr
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# ------------------ CANCEL ------------------

def cancel_ticket(pnr, reason, cancel_date):
    """Cancel a booking by PNR number."""
    session = Session()
    try:
        booking = session.query(Booking).filter_by(pnr_number=pnr).first()
        if not booking:
            return False
        
        # Update booking status
        booking.status = 'Cancelled'
        
        # Create cancellation record
        new_cancellation = Cancellation(
            booking_id=booking.booking_id,
            cancelled_on=cancel_date,
            reason=reason
        )
        session.add(new_cancellation)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# ------------------ STATUS ------------------

def get_booking_by_pnr(pnr):
    """Get booking details by PNR number."""
    session = Session()
    try:
        booking = session.query(Booking).filter_by(pnr_number=pnr).first()
        if not booking:
            return None
            
        # Get train details
        train = session.query(Train).filter_by(train_id=booking.train_id).first()
        
        # Get ticket details
        tickets = session.query(Ticket).filter_by(booking_id=booking.booking_id).all()
        
        # Create a dictionary of booking details
        booking_details = {
            'booking_id': booking.booking_id,
            'pnr_number': booking.pnr_number,
            'train_number': train.train_number,
            'train_name': train.train_name,
            'travel_date': booking.travel_date.strftime('%Y-%m-%d'),
            'booking_date': booking.booking_date.strftime('%Y-%m-%d'),
            'status': booking.status,
            'passengers': [
                {
                    'name': ticket.passenger_name,
                    'age': ticket.age,
                    'gender': ticket.gender,
                }
                for ticket in tickets
            ]
        }
        
        return booking_details
    finally:
        session.close()

# ------------------ ADMIN USER MANAGEMENT ------------------

def get_all_users():
    """Get a list of all users."""
    session = Session()
    try:
        users = session.query(User).all()
        return [(user.username, user.password) for user in users]
    finally:
        session.close()

def update_user_password(username, new_password):
    """Update a user's password."""
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            raise ValueError("User not found")
        
        user.password = new_password
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_user_from_db(username):
    """Delete a user from the database."""
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            raise ValueError("User not found")
        
        # Check if user has any bookings
        bookings = session.query(Booking).filter_by(user_id=user.user_id).all()
        for booking in bookings:
            # Delete related tickets
            session.query(Ticket).filter_by(booking_id=booking.booking_id).delete()
            # Delete related cancellations
            session.query(Cancellation).filter_by(booking_id=booking.booking_id).delete()
            # Delete booking
            session.delete(booking)
        
        # Delete user
        session.delete(user)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# ------------------ ADMIN TRAIN MANAGEMENT ------------------

def add_train(train_number, train_name, source_id, destination_id, departure_time, arrival_time, travel_days):
    """Add a new train to the database."""
    session = Session()
    try:
        new_train = Train(
            train_number=train_number,
            train_name=train_name,
            source_id=source_id,
            destination_id=destination_id,
            departure_time=departure_time,
            arrival_time=arrival_time,
            travel_days=travel_days
        )
        session.add(new_train)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_train(train_id, train_name=None, source_id=None, destination_id=None, 
                departure_time=None, arrival_time=None, travel_days=None):
    """Update train information."""
    session = Session()
    try:
        train = session.query(Train).filter_by(train_id=train_id).first()
        if not train:
            raise ValueError("Train not found")
        
        if train_name:
            train.train_name = train_name
        if source_id:
            train.source_id = source_id
        if destination_id:
            train.destination_id = destination_id
        if departure_time:
            train.departure_time = departure_time
        if arrival_time:
            train.arrival_time = arrival_time
        if travel_days:
            train.travel_days = travel_days
            
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_train(train_id):
    """Delete a train from the database."""
    session = Session()
    try:
        train = session.query(Train).filter_by(train_id=train_id).first()
        if not train:
            raise ValueError("Train not found")
        
        # Check if there are any active bookings for this train
        active_bookings = session.query(Booking).filter_by(
            train_id=train_id, status='Confirmed'
        ).count()
        
        if active_bookings > 0:
            raise ValueError("Cannot delete train with active bookings")
        
        # Delete the train
        session.delete(train)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# ------------------ STATION MANAGEMENT ------------------

def add_station(station_name):
    """Add a new station to the database."""
    session = Session()
    try:
        new_station = Station(station_name=station_name)
        session.add(new_station)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_all_stations():
    """Get a list of all stations."""
    session = Session()
    try:
        stations = session.query(Station).all()
        return [(station.station_id, station.station_name) for station in stations]
    finally:
        session.close()