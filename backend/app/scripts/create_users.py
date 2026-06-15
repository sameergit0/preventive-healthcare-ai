import random
from datetime import date, timedelta

from app.db import sessionLocal
from app.models import User,Profile,Lifestyle, MedicalHistory, HealthMetric
from app.core import hash_password

from sqlalchemy import text

def clear_database(db):
    """
    Safely clears all records and resets ID sequences using TRUNCATE RESTART IDENTITY.
    """
    print("Clearing database and resetting ID sequences...")
    try:
        # Dynamic table discovery from Base metadata
        # We need to truncate in an order that respects foreign keys, or use CASCADE
        tables = ["health_metrics", "medical_history", "lifestyles", "profiles", "users"]
        for table in tables:
            db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
        db.commit()
        print("Database cleared and IDs reset to 1.")
    except Exception as e:
        db.rollback()
        print(f"Error clearing database: {e}")

def create_dummy_data(count=500):
    """
    Generates 500 unique users with organic, sparse data.
    - Uses 500 unique first names + random surnames.
    - Randomly leaves fields as None for a more realistic look.
    - Generates 10-15 random logs per user since April 1st, 2026.
    """
    db = sessionLocal()
    
    # First, clear the database and reset IDs
    clear_database(db)
    
    print(f"Starting creation of {count} dummy users with organic data and surnames...")
    
    # 500 Unique First Names
    FIRST_NAMES = [
        "Aarav", "Aarush", "Aayush", "Abhay", "Abhinav", "Abhishek", "Aditya", "Advaith", "Advik", "Agastya",
        "Ajay", "Akash", "Akhil", "Akshay", "Aman", "Amar", "Amartya", "Amit", "Amol", "Amrit",
        "Anand", "Anant", "Anay", "Angad", "Aniket", "Anil", "Aniruddh", "Anish", "Ankit", "Ankur",
        "Anmol", "Ansh", "Anshul", "Anuj", "Anupam", "Anurag", "Arav", "Arjun", "Arnav", "Aryan",
        "Ashish", "Ashok", "Ashutosh", "Ashwin", "Atul", "Avinash", "Ayush", "Balram", "Bharat", "Bhaskar",
        "Bhuvan", "Chaitanya", "Chandan", "Chetan", "Chirag", "Daksh", "Damodar", "Darpan", "Darshan", "Deepak",
        "Deepankar", "Deepansh", "Dev", "Devansh", "Deven", "Devesh", "Dhanush", "Dhaval", "Dheeraj", "Dhruv",
        "Digvijay", "Dilip", "Dinesh", "Divit", "Divyansh", "Eeshwar", "Eklavya", "Gagan", "Ganesh", "Gaurang",
        "Gaurav", "Gautam", "Girish", "Gopal", "Govind", "Gulshan", "Gunjan", "Hardik", "Hari", "Harish",
        "Harit", "Harivansh", "Harsh", "Harshal", "Harshit", "Hemant", "Himanshu", "Hitansh", "Hriday", "Hrishikesh",
        "Inder", "Indrajeet", "Ishaan", "Ishwar", "Jagdish", "Jai", "Jaideep", "Jatin", "Javed", "Jay",
        "Jayant", "Jayesh", "Jeet", "Jitendra", "Jivaj", "Kabir", "Kailash", "Kalpesh", "Kalyan", "Kamal",
        "Kamlesh", "Kanak", "Kanav", "Kanishk", "Kapil", "Karan", "Kartik", "Kashyap", "Kaushal", "Kavi",
        "Kavin", "Kavish", "Kedar", "Keshav", "Ketan", "Keval", "Kiran", "Kirtan", "Kishore", "Kovid",
        "Krish", "Krishna", "Krunal", "Kshitij", "Kuldeep", "Kunal", "Kush", "Kushagra", "Laksh", "Lakshay",
        "Lakshman", "Lalit", "Lokesh", "Madhav", "Madhu", "Madis", "Mahaveer", "Mahendra", "Mahesh", "Mainak",
        "Manan", "Manas", "Manav", "Mandeep", "Mangal", "Mangesh", "Mani", "Manik", "Manish", "Manit",
        "Manjeet", "Manjunath", "Manmohan", "Manoj", "Manthan", "Manu", "Mayank", "Mayur", "Mehul", "Milind",
        "Mithun", "Mohan", "Mohit", "Mridul", "Mukesh", "Mukund", "Murari", "Nakul", "Naman", "Namit",
        "Nand", "Nandan", "Narendra", "Naresh", "Navneet", "Neel", "Neeraj", "Nikhil", "Nilay", "Nilesh",
        "Nimish", "Nipun", "Niraj", "Nirav", "Nirmal", "Nishant", "Nishit", "Nitish", "Ojas", "Om",
        "Omkar", "Onkar", "Padmanabh", "Palaash", "Pallav", "Pankaj", "Parag", "Param", "Paras", "Paritosh",
        "Parth", "Parv", "Pavan", "Phani", "Piyush", "Prabal", "Prabhakar", "Prabhat", "Prabhu", "Pradip",
        "Pradyumna", "Prafull", "Pragun", "Prahalad", "Prajwal", "Prakash", "Pramod", "Pran", "Pranay", "Praneel",
        "Praneet", "Pranjal", "Pranshu", "Prasad", "Prasanna", "Prashant", "Pratap", "Prateek", "Prathamesh", "Pratik",
        "Pratush", "Praval", "Praveen", "Pravin", "Prayas", "Preet", "Prem", "Prithvi", "Priyansh", "Puneet",
        "Punit", "Pushkar", "Raahil", "Rachit", "Raghav", "Raghu", "Rahul", "Rajat", "Rajdeep", "Rajeev",
        "Rajendra", "Rajesh", "Rajit", "Rajkumar", "Rajnish", "Rakesh", "Rakshit", "Ram", "Ramakant", "Raman",
        "Ramandeep", "Ramesh", "Ranbir", "Randhir", "Ranganath", "Ranjan", "Ranjeet", "Ranjit", "Ranveer", "Ranvijay",
        "Rashesh", "Ratan", "Ratish", "Raveen", "Ravi", "Ravindra", "Rishi", "Rishit", "Ritesh", "Ritvik",
        "Riyaan", "Rohan", "Rohit", "Ronit", "Rudra", "Rupesh", "Rushil", "Saahil", "Sachet", "Sachin",
        "Sagar", "Sahil", "Saket", "Saksham", "Samar", "Samarth", "Sambhav", "Sameer", "Samir", "Samrat",
        "Sanchit", "Sandeep", "Sandesh", "Sanjay", "Sanjeev", "Sanjiv", "Sanket", "Santosh", "Sapan", "Sarang",
        "Saras", "Sarath", "Sarthak", "Sarvad", "Sarvesh", "Satish", "Satya", "Satyajeet", "Satyam", "Saurabh",
        "Saurav", "Savit", "Sayan", "Shakti", "Shantanu", "Sharad", "Shashank", "Shashwat", "Shaurya", "Shekhar",
        "Shikhar", "Shirish", "Shishir", "Shiv", "Shivam", "Shiven", "Shivraj", "Shlok", "Shobhit", "Shravan",
        "Shray", "Shrey", "Shreyas", "Shreyash", "Shrihan", "Shrijan", "Shubham", "Shlok", "Siddharth", "Soham",
        "Sohan", "Somesh", "Sparsh", "Srijan", "Subhash", "Sudeep", "Sudhanshu", "Sudhir", "Suhas", "Sujit",
        "Sukhdev", "Sumer", "Sumit", "Sunder", "Sunil", "Suraj", "Suresh", "Surya", "Suryansh", "Sushant",
        "Sushil", "Sushrut", "Swayam", "Tanay", "Tanish", "Tanishq", "Tanmay", "Tanuj", "Tapan", "Tapas",
        "Tarun", "Tejas", "Tejesh", "Trishul", "Tushar", "Uday", "Udit", "Ujjwal", "Umang", "Umesh",
        "Unmesh", "Upendra", "Utkarsh", "Utsav", "Vaibhav", "Vansh", "Varad", "Vardhan", "Varun", "Vasant",
        "Vasudev", "Vatsal", "Ved", "Vedant", "Vedshri", "Veer", "Venkat", "Vibhas", "Vibhu", "Vidit",
        "Vidur", "Vihan", "Vijay", "Vikas", "Vikram", "Vikrant", "Vimal", "Vinay", "Vineet", "Vinod",
        "Vipin", "Viplav", "Vipul", "Viraj", "Vishal", "Vishesh", "Vishnu", "Vishwa", "Vishwas", "Vishwesh",
        "Vivan", "Vivek", "Vraj", "Vyom", "Yadunand", "Yash", "Yashaswi", "Yashpal", "Yashwardhan", "Yatin",
        "Yogesh", "Yogit", "Yug", "Yuvan", "Yuvraj", "Zaid", "Zayan", "Aadhya", "Aahana", "Aakriti",
        "Aaradhya", "Aarohi", "Aarti", "Aastha", "Aayushi", "Abha", "Abhilasha", "Aditi", "Aishwarya", "Akansha",
        "Akshara", "Alka", "Amita", "Amoli", "Amrita", "Ananya", "Anchal", "Anika", "Anjali", "Anjana",
        "Ankita", "Anshika", "Anupama", "Anuradha", "Anushka", "Anvi", "Aparna", "Archana", "Arpita", "Arunima",
        "Asha", "Ashini", "Ashmita", "Ashna", "Ashwini", "Asmita", "Avani", "Avantika", "Avni", "Ayushi",
        "Barkha", "Beena", "Bhakti", "Bhavana", "Bhavika", "Bhavini", "Bhavya", "Bhumika", "Binita", "Chahat",
        "Chaitali", "Chanchal", "Charu", "Chetana", "Chhavi", "Chitra", "Damini", "Darshana", "Deepa", "Deepika",
        "Deepshikha", "Deepti", "Devanshi", "Devi", "Devika", "Dhara", "Dharini", "Dhriti", "Diksha", "Dipali",
        "Disha", "Diti", "Divya", "Drishti", "Durga", "Ekta", "Esha", "Faluni", "Falguni", "Gargi",
        "Garima", "Gauri", "Gautami", "Gayatri", "Geeta", "Geetika", "Gia", "Ginni", "Girishma", "Gitali",
        "Gitanjali", "Greeshma", "Gul", "Gunjan", "Hansa", "Harini", "Harita", "Harshada", "Harshita", "Heena",
        "Hema", "Hemangi", "Hemani", "Hemlata", "Hiral", "Hiyana", "Ira", "Isha", "Ishani", "Ishita",
        "Iva", "Jagriti", "Janaki", "Janvi", "Jaya", "Jayna", "Jayanti", "Jeevika", "Jhalak", "Jhanvi",
        "Jigisha", "Juhi", "Jyoti", "Jyotsna", "Kajal", "Kala", "Kalpana", "Kamala", "Kamini", "Kanak",
        "Kanchan", "Kanika", "Kanishka", "Kanti", "Karishma", "Kashish", "Kasturi", "Kavita", "Kavya", "Khushi",
        "Khyati", "Kinjal", "Kiran", "Kirti", "Komal", "Koyal", "Krisha", "Krishna", "Kritika", "Kruti",
        "Kshama", "Kumud", "Kunti", "Kushali", "Kusum", "Lalita", "Lata", "Laxmi", "Leela", "Lekha",
        "Lipika", "Lopa", "Madhavi", "Madhu", "Madhubala", "Madhuri", "Mahima", "Maina", "Malati", "Malini",
        "Malsi", "Mamta", "Manasi", "Manini", "Manisha", "Manjari", "Manju", "Manjusha", "Manorama", "Mansi",
        "Manyata", "Maya", "Mayuri", "Meena", "Meenakshi", "Megha", "Mehal", "Meher", "Mehul", "Minal",
        "Minati", "Mira", "Mita", "Mitali", "Mithila", "Mohini", "Mona", "Monika", "Mridula", "Mukta",
        "Muna", "Muskan", "Mythili", "Naina", "Nalini", "Namita", "Namrata", "Nanda", "Nandini", "Nandita",
        "Narmada", "Naveena", "Navya", "Nayana", "Neela", "Neelam", "Neeraja", "Neeru", "Neha", "Nehal",
        "Netra", "Nidhi", "Niharika", "Nikita", "Nilam", "Nilima", "Nina", "Nirupama", "Nisha", "Nishita",
        "Niti", "Nitya", "Nivedita", "Niyati", "Nupur", "Nutan", "Ojaswi", "Omana", "Padma", "Padmini",
        "Pallavi", "Pankhuri", "Paridhi", "Pari", "Parnika", "Parul", "Parvati", "Payal", "Pia", "Pinky",
        "Pooja", "Poonam", "Poorvi", "Prabha", "Prachi", "Pragati", "Pragya", "Pramila", "Pranjal", "Pratibha",
        "Pratima", "Pratishtha", "Preeti", "Prerna", "Priti", "Priya", "Priyanka", "Puja", "Punita", "Purnima",
        "Purva", "Pushpa", "Rachana", "Radha", "Radhika", "Ragini", "Rajani", "Rajeshwari", "Rajni", "Rakhi",
        "Rakshita", "Rama", "Ramya", "Rani", "Ranjana", "Ranjita", "Rashmi", "Rashmika", "Rati", "Ratna",
        "Raveena", "Reema", "Rekha", "Renu", "Renuka", "Reshma", "Revati", "Richa", "Riddhi", "Rina",
        "Rini", "Rishika", "Rita", "Ritu", "Riya", "Rohini", "Roma", "Roopa", "Roshni", "Ruchi",
        "Ruchira", "Ruhani", "Ruma", "Rupa", "Rupali", "Sabina", "Sadhana", "Sagarika", "Sahiba", "Sakshi",
        "Saloni", "Samyukta", "Sana", "Sandhya", "Sangeeta", "Sania", "Sanjana", "Sanjita", "Sanya", "Sapna",
        "Sara", "Sarala", "Saraswati", "Sarika", "Sarita", "Saroj", "Saru", "Sashi", "Sasmita", "Sati",
        "Saumya", "Savita", "Savtri", "Seema", "Sejal", "Shaila", "Shailaja", "Shakti", "Shalini", "Shamita",
        "Shanti", "Sharada", "Sharda", "Sharmila", "Shashi", "Sheetal", "Shikha", "Shila", "Shilpa", "Shital",
        "Shivani", "Shobha", "Shobhana", "Shraddha", "Shravani", "Shree", "Shreya", "Shruti", "Shubha", "Shubhangi",
        "Shweta", "Sia", "Siddhi", "Simran", "Sindhu", "Sita", "Siya", "Smaranika", "Smita", "Smriti",
        "Sneha", "Snigdha", "Soma", "Sonal", "Sonali", "Sonam", "Sonia", "Sudha", "Sujata", "Sukanya",
        "Suman", "Sumitra", "Sunayana", "Sunita", "Suniti", "Supriya", "Surabhi", "Surbhi", "Sushma", "Sushmita",
        "Swati", "Tanu", "Tanuja", "Tanvi", "Tanya", "Tara", "Trupti", "Tulsi", "Uma", "Ume",
        "Unnati", "Upasana", "Urmila", "Urshila", "Urvashi", "Urvi", "Usha", "Ushma", "Utpala", "Vaishali",
        "Vandana", "Vani", "Vanita", "Varsha", "Vasudha", "Vedika", "Veena", "Vibha", "Vidya", "Vimala",
        "Vinita", "Vinodini", "Vrinda", "Yamini", "Yashoda", "Yashaswini", "Yuvika", "Zoya", "Zara", "Zeenat"
    ]
    
    LAST_NAMES = [
        "Kumar", "Sharma", "Singh", "Verma", "Patel", "Gupta", "Das", "Yadav", "Reddy", "Khan",
        "Joshi", "Bhatt", "Mehra", "Kapoor", "Chopra", "Malhotra", "Goel", "Bansal", "Aggarwal", "Mittal"
    ]
    
    # Start date for logs: April 1, 2026
    START_DATE = date(2026, 4, 1)
    TODAY = date.today()
    DAYS_SINCE_START = (TODAY - START_DATE).days

    try:
        for i in range(1, count + 1):
            # Pick first name sequentially
            first = FIRST_NAMES[(i-1) % len(FIRST_NAMES)]
            surname = random.choice(LAST_NAMES)
            
            # Uniqueness handling for email
            email_base = first.lower()
            if i > len(FIRST_NAMES):
                email_base = f"{email_base}{i // len(FIRST_NAMES)}"
            
            email = f"{email_base}@gmail.com"
            raw_password = f"{first.capitalize()}@123"
            hashed_pwd = hash_password(raw_password)
            
            # Check if user already exists
            existing = db.query(User).filter(User.email == email).first()
            
            if existing:
                # Update profile name if it doesn't have a surname
                if existing.profile:
                    existing.profile.full_name = f"{first.capitalize()} {surname}"
                    db.add(existing.profile)
                continue
                
            # 1. Create User
            new_user = User(
                email=email,
                hash_password=hashed_pwd,
                timezone=random.choice(["UTC", "Asia/Kolkata", "America/New_York", "Europe/London"])
            )
            db.add(new_user)
            db.flush() 
            
            # 2. Create Profile (Mandatory fields must be filled to avoid API errors)
            profile = Profile(
                user_id=new_user.id,
                full_name=f"{first.capitalize()} {surname}",
                age=random.randint(18, 75),
                gender=random.choice(['M', 'F']),
                weight=round(random.uniform(50.0, 110.0), 1),
                height=round(random.uniform(155.0, 190.0), 1),
                waist_cm=random.choice([round(random.uniform(70.0, 110.0), 1), None]),
                goal=random.choice([
                    'Weight Loss', 'Weight Gain', 'Muscle Building', 
                    'Maintain Fitness', 'Improve Sleep', 'Reduce Stress'
                ])
            )
            db.add(profile)
            
            # 3. Create Lifestyle Profile (Randomly skip some fields)
            lifestyle = Lifestyle(
                user_id=new_user.id,
                tobacco_type=random.choice(["never", "daily", "weekly", "occasionally", "former", None]),
                passive_smoke=random.choice([True, False, None]),
                alcohol_freq=random.choice(["never","rarely", "sometimes", "often", "daily", None]),
                alcohol_binge=random.choice([True, False, None]),
                stress_level=random.choice([random.randint(1, 5), None]),
                work_life_balance=random.choice([random.randint(1, 5), None]),
                screen_time_hours=random.choice([round(random.uniform(2.0, 10.0), 1), None])
            )
            db.add(lifestyle)
            
            # 4. Create Medical History (Mostly False/None)
            medical = MedicalHistory(
                user_id=new_user.id,
                diabetes=random.choice([True, False, False, False, None]),
                bp=random.choice([True, False, False, None]),
                high_cholesterol=random.choice([True, False, False, None]),
                heart_disease=random.choice([True, False, False, False, None]),
                asthma=random.choice([True, False, False, False, None])
            )
            db.add(medical)
            
            # 5. Create Health Metrics (10-15 random logs since April 1, 2026)
            num_logs = random.randint(10, 15)
            # Pick random unique dates
            if DAYS_SINCE_START > num_logs:
                log_offsets = random.sample(range(DAYS_SINCE_START + 1), num_logs)
            else:
                log_offsets = range(DAYS_SINCE_START + 1)
                
            for offset in log_offsets:
                log_date = START_DATE + timedelta(days=offset)
                
                # Generate random food log
                meals = []
                if random.random() > 0.2: # 80% chance of having some food logs
                    if random.choice([True, False, True]): # 66% chance of having breakfast
                        meals.append({
                            "meal": "breakfast", 
                            "items": random.sample(["Poha", "Tea", "Eggs", "Toast", "Oats", "Fruit bowl", "Idli", "Dosa"], random.randint(1, 3))
                        })
                    if random.choice([True, False, True]): # 66% chance of having lunch
                        meals.append({
                            "meal": "lunch", 
                            "items": random.sample(["Salad", "Sandwich", "Rice", "Dal", "Roti", "Paneer", "Chicken", "Curry"], random.randint(1, 3))
                        })
                    if random.choice([True, False, True]): # 66% chance of having dinner
                        meals.append({
                            "meal": "dinner", 
                            "items": random.sample(["Soup", "Grilled Fish", "Vegetable Stir-fry", "Pasta", "Quinoa", "Tacos"], random.randint(1, 3))
                        })

                metric = HealthMetric(
                    user_id=new_user.id,
                    steps=random.choice([random.randint(1000, 18000), None]),
                    sleep_hours=random.choice([round(random.uniform(4.0, 10.0), 1), None]),
                    water_intake=random.choice([round(random.uniform(0.5, 4.5), 1), None]),
                    food_log=meals,
                    sleep_quality=random.choice(['poor', 'average', 'good', 'excellent', None]),
                    activity_minutes=random.choice([random.randint(0, 150), None]),
                    nutrition_sugar=random.choice([round(random.uniform(5.0, 80.0), 1), None]),
                    nutrition_fruits=random.choice([random.randint(0, 6), None]),
                    log_date=log_date
                )
                db.add(metric)
            
            if i % 50 == 0:
                db.commit()
                print(f"Successfully created {i} users...")
                
        db.commit()
        print(f"\n--- DONE ---")
        print(f"Created {count} users with organic data and surnames.")
        print(f"Email: name@gmail.com | Pass: Name@123")
        print(f"Logs: 10-15 random entries per user since April 1, 2026.")
        print("-" * 50)
        
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_dummy_data()
