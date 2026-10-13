"""
demo_dataset.py
BMV3 Child Development Center Management System
Comprehensive dataset definitions and seeding routines for:
1. Historical School Year 2024-2025 (Completed / Archived)
2. 60 Realistic Fictional Filipino Daycare Pupils (30 Morning Shift, 30 Afternoon Shift)
3. Rich Historical Attendance, Nutrition, BMI, ECCD Milestone, and Engagement Records
4. 60 Ready-to-Use Demo Parent Accounts (parent001 to parent060) with mandatory First-Login Password Change
5. Restricted Credential CSV Generation (bmv3_demo_parent_credentials.csv)
"""

import os
import csv
import random
import datetime
from decimal import Decimal
from pathlib import Path
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from apps.core.models import (
    SchoolYear, Child, UserProfile, AttendanceRecord,
    NutritionRecord, EngagementRecord, BMIRecord,
    ECCDAssessment, ECCDMilestone, ECCDMilestoneScore,
    MilestoneRecord, Activity, StudentActivityCompletion,
    CenterSettings
)

# 60 Realistic, Fictional Filipino Child Profiles (30 Morning, 30 Afternoon)
CHILDREN_PROFILES = [
    # ------------------ MORNING SHIFT (30 Children) ------------------
    {
        "account_num": 1,
        "username": "parent001",
        "first_name": "Juan Gabriel",
        "middle_initial": "S",
        "last_name": "Santos",
        "age": 4,
        "dob": "2020-04-12",
        "gender": "Male",
        "shift": "Morning",
        "street": "14 Sampaguita St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Elena",
        "mother_last_name": "Santos",
        "mother_phone": "0917-555-0101",
        "mother_email": "elena.santos@bmv3.demo.local",
        "father_first_name": "Roberto",
        "father_last_name": "Santos",
        "father_phone": "0918-555-0101",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.8,
        "height": 96.5,
    },
    {
        "account_num": 2,
        "username": "parent002",
        "first_name": "Maria Angela",
        "middle_initial": "R",
        "last_name": "Reyes",
        "age": 4,
        "dob": "2020-07-25",
        "gender": "Female",
        "shift": "Morning",
        "street": "28 Rosal St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Corazon",
        "mother_last_name": "Reyes",
        "mother_phone": "0917-555-0102",
        "mother_email": "corazon.reyes@bmv3.demo.local",
        "father_first_name": "Danilo",
        "father_last_name": "Reyes",
        "father_phone": "0918-555-0102",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.2,
        "height": 95.0,
    },
    {
        "account_num": 3,
        "username": "parent003",
        "first_name": "Mateo Luis",
        "middle_initial": "C",
        "last_name": "Cruz",
        "age": 4,
        "dob": "2020-02-18",
        "gender": "Male",
        "shift": "Morning",
        "street": "5 Ilang-Ilang St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Lourdes",
        "mother_last_name": "Cruz",
        "mother_phone": "0917-555-0103",
        "mother_email": "lourdes.cruz@bmv3.demo.local",
        "father_first_name": "Eduardo",
        "father_last_name": "Cruz",
        "father_phone": "0918-555-0103",
        "allergies": "Peanuts",
        "health_conditions": "Mild Allergic Rhinitis",
        "weight": 15.6,
        "height": 98.2,
    },
    {
        "account_num": 4,
        "username": "parent004",
        "first_name": "Sofia Beatrice",
        "middle_initial": "G",
        "last_name": "Garcia",
        "age": 3,
        "dob": "2021-03-09",
        "gender": "Female",
        "shift": "Morning",
        "street": "42 Gumamela St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Rowena",
        "mother_last_name": "Garcia",
        "mother_phone": "0917-555-0104",
        "mother_email": "rowena.garcia@bmv3.demo.local",
        "father_first_name": "Ferdinand",
        "father_last_name": "Garcia",
        "father_phone": "0918-555-0104",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 13.5,
        "height": 92.4,
    },
    {
        "account_num": 5,
        "username": "parent005",
        "first_name": "Lucas Antonio",
        "middle_initial": "B",
        "last_name": "Bautista",
        "age": 4,
        "dob": "2020-09-14",
        "gender": "Male",
        "shift": "Morning",
        "street": "19 Ditas St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Maricel",
        "mother_last_name": "Bautista",
        "mother_phone": "0917-555-0105",
        "mother_email": "maricel.bautista@bmv3.demo.local",
        "father_first_name": "Arnel",
        "father_last_name": "Bautista",
        "father_phone": "0918-555-0105",
        "allergies": "Dust mite sensitivity",
        "health_conditions": "Asthma (Mild)",
        "weight": 14.5,
        "height": 96.0,
    },
    {
        "account_num": 6,
        "username": "parent006",
        "first_name": "Althea Mae",
        "middle_initial": "M",
        "last_name": "Mendoza",
        "age": 4,
        "dob": "2020-06-30",
        "gender": "Female",
        "shift": "Morning",
        "street": "8 Cattleya St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Jennifer",
        "mother_last_name": "Mendoza",
        "mother_phone": "0917-555-0106",
        "mother_email": "jennifer.mendoza@bmv3.demo.local",
        "father_first_name": "Noel",
        "father_last_name": "Mendoza",
        "father_phone": "0918-555-0106",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.0,
        "height": 94.8,
    },
    {
        "account_num": 7,
        "username": "parent007",
        "first_name": "Gabriel Miguel",
        "middle_initial": "R",
        "last_name": "Ramos",
        "age": 5,
        "dob": "2019-11-22",
        "gender": "Male",
        "shift": "Morning",
        "street": "33 Waling-Waling St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Carmela",
        "mother_last_name": "Ramos",
        "mother_phone": "0917-555-0107",
        "mother_email": "carmela.ramos@bmv3.demo.local",
        "father_first_name": "Richard",
        "father_last_name": "Ramos",
        "father_phone": "0918-555-0107",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 16.4,
        "height": 101.5,
    },
    {
        "account_num": 8,
        "username": "parent008",
        "first_name": "Samantha Nicole",
        "middle_initial": "D",
        "last_name": "Dela Cruz",
        "age": 4,
        "dob": "2020-05-17",
        "gender": "Female",
        "shift": "Morning",
        "street": "12 Everlasting St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Maria Fe",
        "mother_last_name": "Dela Cruz",
        "mother_phone": "0917-555-0108",
        "mother_email": "mariafe.delacruz@bmv3.demo.local",
        "father_first_name": "Renato",
        "father_last_name": "Dela Cruz",
        "father_phone": "0918-555-0108",
        "allergies": "Seafood",
        "health_conditions": "None reported",
        "weight": 14.7,
        "height": 96.2,
    },
    {
        "account_num": 9,
        "username": "parent009",
        "first_name": "Ethan James",
        "middle_initial": "F",
        "last_name": "Flores",
        "age": 4,
        "dob": "2020-08-04",
        "gender": "Male",
        "shift": "Morning",
        "street": "25 Bougainvillea St.",
        "purok": "Purok 5",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Glenda",
        "mother_last_name": "Flores",
        "mother_phone": "0917-555-0109",
        "mother_email": "glenda.flores@bmv3.demo.local",
        "father_first_name": "Albert",
        "father_last_name": "Flores",
        "father_phone": "0918-555-0109",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.1,
        "height": 97.4,
    },
    {
        "account_num": 10,
        "username": "parent010",
        "first_name": "Chloe Danielle",
        "middle_initial": "A",
        "last_name": "Aquino",
        "age": 3,
        "dob": "2021-01-20",
        "gender": "Female",
        "shift": "Morning",
        "street": "17 Camia St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Diana",
        "mother_last_name": "Aquino",
        "mother_phone": "0917-555-0110",
        "mother_email": "diana.aquino@bmv3.demo.local",
        "father_first_name": "Mark",
        "father_last_name": "Aquino",
        "father_phone": "0918-555-0110",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 13.8,
        "height": 93.5,
    },
    {
        "account_num": 11,
        "username": "parent011",
        "first_name": "Nathan Alexander",
        "middle_initial": "V",
        "last_name": "Villanueva",
        "age": 4,
        "dob": "2020-10-11",
        "gender": "Male",
        "shift": "Morning",
        "street": "30 Santan St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Sheryl",
        "mother_last_name": "Villanueva",
        "mother_phone": "0917-555-0111",
        "mother_email": "sheryl.villanueva@bmv3.demo.local",
        "father_first_name": "Jason",
        "father_last_name": "Villanueva",
        "father_phone": "0918-555-0111",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.0,
        "height": 96.8,
    },
    {
        "account_num": 12,
        "username": "parent012",
        "first_name": "Princess Joy",
        "middle_initial": "C",
        "last_name": "Castillo",
        "age": 4,
        "dob": "2020-03-15",
        "gender": "Female",
        "shift": "Morning",
        "street": "7 Adelfa St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Marilou",
        "mother_last_name": "Castillo",
        "mother_phone": "0917-555-0112",
        "mother_email": "marilou.castillo@bmv3.demo.local",
        "father_first_name": "Victor",
        "father_last_name": "Castillo",
        "father_phone": "0918-555-0112",
        "allergies": "Eggs",
        "health_conditions": "None reported",
        "weight": 14.3,
        "height": 95.3,
    },
    {
        "account_num": 13,
        "username": "parent013",
        "first_name": "Ezekiel John",
        "middle_initial": "T",
        "last_name": "Tolentino",
        "age": 4,
        "dob": "2020-12-05",
        "gender": "Male",
        "shift": "Morning",
        "street": "15 Cadena de Amor St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Kristine",
        "mother_last_name": "Tolentino",
        "mother_phone": "0917-555-0113",
        "mother_email": "kristine.tolentino@bmv3.demo.local",
        "father_first_name": "Dennis",
        "father_last_name": "Tolentino",
        "father_phone": "0918-555-0113",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.9,
        "height": 96.1,
    },
    {
        "account_num": 14,
        "username": "parent014",
        "first_name": "Jasmine Rose",
        "middle_initial": "M",
        "last_name": "Mercado",
        "age": 5,
        "dob": "2019-10-28",
        "gender": "Female",
        "shift": "Morning",
        "street": "21 Jasmin St.",
        "purok": "Purok 5",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Rosalinda",
        "mother_last_name": "Mercado",
        "mother_phone": "0917-555-0114",
        "mother_email": "rosalinda.mercado@bmv3.demo.local",
        "father_first_name": "Ramon",
        "father_last_name": "Mercado",
        "father_phone": "0918-555-0114",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 16.2,
        "height": 100.8,
    },
    {
        "account_num": 15,
        "username": "parent015",
        "first_name": "Daniel Joaquin",
        "middle_initial": "N",
        "last_name": "Navarro",
        "age": 4,
        "dob": "2020-04-03",
        "gender": "Male",
        "shift": "Morning",
        "street": "11 Champaca St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Lorena",
        "mother_last_name": "Navarro",
        "mother_phone": "0917-555-0115",
        "mother_email": "lorena.navarro@bmv3.demo.local",
        "father_first_name": "Gilbert",
        "father_last_name": "Navarro",
        "father_phone": "0918-555-0115",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.3,
        "height": 97.5,
    },
    {
        "account_num": 16,
        "username": "parent016",
        "first_name": "Andrea Denise",
        "middle_initial": "P",
        "last_name": "Pascual",
        "age": 4,
        "dob": "2020-06-18",
        "gender": "Female",
        "shift": "Morning",
        "street": "39 Dalia St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Annalyn",
        "mother_last_name": "Pascual",
        "mother_phone": "0917-555-0116",
        "mother_email": "annalyn.pascual@bmv3.demo.local",
        "father_first_name": "Edgar",
        "father_last_name": "Pascual",
        "father_phone": "0918-555-0116",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.4,
        "height": 95.8,
    },
    {
        "account_num": 17,
        "username": "parent017",
        "first_name": "Christian Paul",
        "middle_initial": "S",
        "last_name": "Salazar",
        "age": 3,
        "dob": "2021-05-12",
        "gender": "Male",
        "shift": "Morning",
        "street": "16 Ilang-Ilang St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Emelita",
        "mother_last_name": "Salazar",
        "mother_phone": "0917-555-0117",
        "mother_email": "emelita.salazar@bmv3.demo.local",
        "father_first_name": "Paulino",
        "father_last_name": "Salazar",
        "father_phone": "0918-555-0117",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 13.7,
        "height": 93.0,
    },
    {
        "account_num": 18,
        "username": "parent018",
        "first_name": "Angel Louise",
        "middle_initial": "D",
        "last_name": "De Guzman",
        "age": 4,
        "dob": "2020-08-29",
        "gender": "Female",
        "shift": "Morning",
        "street": "24 Rosal St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Marissa",
        "mother_last_name": "De Guzman",
        "mother_phone": "0917-555-0118",
        "mother_email": "marissa.deguzman@bmv3.demo.local",
        "father_first_name": "Joel",
        "father_last_name": "De Guzman",
        "father_phone": "0918-555-0118",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.6,
        "height": 96.0,
    },
    {
        "account_num": 19,
        "username": "parent019",
        "first_name": "Noah Sebastian",
        "middle_initial": "O",
        "last_name": "Ocampo",
        "age": 4,
        "dob": "2020-01-14",
        "gender": "Male",
        "shift": "Morning",
        "street": "35 Gumamela St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Regina",
        "mother_last_name": "Ocampo",
        "mother_phone": "0917-555-0119",
        "mother_email": "regina.ocampo@bmv3.demo.local",
        "father_first_name": "Nestor",
        "father_last_name": "Ocampo",
        "father_phone": "0918-555-0119",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.5,
        "height": 98.0,
    },
    {
        "account_num": 20,
        "username": "parent020",
        "first_name": "Bea Alyssa",
        "middle_initial": "S",
        "last_name": "Samson",
        "age": 4,
        "dob": "2020-07-08",
        "gender": "Female",
        "shift": "Morning",
        "street": "18 Cattleya St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Shirley",
        "mother_last_name": "Samson",
        "mother_phone": "0917-555-0120",
        "mother_email": "shirley.samson@bmv3.demo.local",
        "father_first_name": "Gary",
        "father_last_name": "Samson",
        "father_phone": "0918-555-0120",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.1,
        "height": 95.2,
    },
    {
        "account_num": 21,
        "username": "parent021",
        "first_name": "Liam Matthew",
        "middle_initial": "V",
        "last_name": "Valenzuela",
        "age": 4,
        "dob": "2020-11-19",
        "gender": "Male",
        "shift": "Morning",
        "street": "9 Waling-Waling St.",
        "purok": "Purok 5",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Bernadette",
        "mother_last_name": "Valenzuela",
        "mother_phone": "0917-555-0121",
        "mother_email": "bernadette.valenzuela@bmv3.demo.local",
        "father_first_name": "Felipe",
        "father_last_name": "Valenzuela",
        "father_phone": "0918-555-0121",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.8,
        "height": 96.6,
    },
    {
        "account_num": 22,
        "username": "parent022",
        "first_name": "Kimberly Ann",
        "middle_initial": "R",
        "last_name": "Roxas",
        "age": 5,
        "dob": "2019-12-01",
        "gender": "Female",
        "shift": "Morning",
        "street": "44 Sampaguita St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Clarissa",
        "mother_last_name": "Roxas",
        "mother_phone": "0917-555-0122",
        "mother_email": "clarissa.roxas@bmv3.demo.local",
        "father_first_name": "Manuel",
        "father_last_name": "Roxas",
        "father_phone": "0918-555-0122",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 16.0,
        "height": 101.0,
    },
    {
        "account_num": 23,
        "username": "parent023",
        "first_name": "Jacob Caleb",
        "middle_initial": "P",
        "last_name": "Pineda",
        "age": 3,
        "dob": "2021-04-22",
        "gender": "Male",
        "shift": "Morning",
        "street": "13 Ditas St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Lea",
        "mother_last_name": "Pineda",
        "mother_phone": "0917-555-0123",
        "mother_email": "lea.pineda@bmv3.demo.local",
        "father_first_name": "Christopher",
        "father_last_name": "Pineda",
        "father_phone": "0918-555-0123",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 13.9,
        "height": 93.8,
    },
    {
        "account_num": 24,
        "username": "parent024",
        "first_name": "Hannah Grace",
        "middle_initial": "S",
        "last_name": "Soriano",
        "age": 4,
        "dob": "2020-02-27",
        "gender": "Female",
        "shift": "Morning",
        "street": "22 Everlasting St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Giselle",
        "mother_last_name": "Soriano",
        "mother_phone": "0917-555-0124",
        "mother_email": "giselle.soriano@bmv3.demo.local",
        "father_first_name": "Reynaldo",
        "father_last_name": "Soriano",
        "father_phone": "0918-555-0124",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.5,
        "height": 95.7,
    },
    {
        "account_num": 25,
        "username": "parent025",
        "first_name": "Marcus Dave",
        "middle_initial": "C",
        "last_name": "Corpuz",
        "age": 4,
        "dob": "2020-09-05",
        "gender": "Male",
        "shift": "Morning",
        "street": "31 Bougainvillea St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Teresa",
        "mother_last_name": "Corpuz",
        "mother_phone": "0917-555-0125",
        "mother_email": "teresa.corpuz@bmv3.demo.local",
        "father_first_name": "Dante",
        "father_last_name": "Corpuz",
        "father_phone": "0918-555-0125",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.2,
        "height": 97.2,
    },
    {
        "account_num": 26,
        "username": "parent026",
        "first_name": "Danica Marie",
        "middle_initial": "E",
        "last_name": "Evangelista",
        "age": 4,
        "dob": "2020-05-02",
        "gender": "Female",
        "shift": "Morning",
        "street": "6 Camia St.",
        "purok": "Purok 5",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Leonora",
        "mother_last_name": "Evangelista",
        "mother_phone": "0917-555-0126",
        "mother_email": "leonora.evangelista@bmv3.demo.local",
        "father_first_name": "Rene",
        "father_last_name": "Evangelista",
        "father_phone": "0918-555-0126",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.3,
        "height": 95.0,
    },
    {
        "account_num": 27,
        "username": "parent027",
        "first_name": "Joshua Emmanuel",
        "middle_initial": "C",
        "last_name": "Cortez",
        "age": 4,
        "dob": "2020-03-31",
        "gender": "Male",
        "shift": "Morning",
        "street": "27 Santan St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Irene",
        "mother_last_name": "Cortez",
        "mother_phone": "0917-555-0127",
        "mother_email": "irene.cortez@bmv3.demo.local",
        "father_first_name": "Ruben",
        "father_last_name": "Cortez",
        "father_phone": "0918-555-0127",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.0,
        "height": 96.5,
    },
    {
        "account_num": 28,
        "username": "parent028",
        "first_name": "Patricia Ysabel",
        "middle_initial": "D",
        "last_name": "David",
        "age": 4,
        "dob": "2020-10-24",
        "gender": "Female",
        "shift": "Morning",
        "street": "19 Adelfa St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Yvette",
        "mother_last_name": "David",
        "mother_phone": "0917-555-0128",
        "mother_email": "yvette.david@bmv3.demo.local",
        "father_first_name": "Cesar",
        "father_last_name": "David",
        "father_phone": "0918-555-0128",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.6,
        "height": 95.9,
    },
    {
        "account_num": 29,
        "username": "parent029",
        "first_name": "Kyle Justine",
        "middle_initial": "M",
        "last_name": "Magpantay",
        "age": 5,
        "dob": "2019-11-08",
        "gender": "Male",
        "shift": "Morning",
        "street": "38 Cadena de Amor St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Rosalie",
        "mother_last_name": "Magpantay",
        "mother_phone": "0917-555-0129",
        "mother_email": "rosalie.magpantay@bmv3.demo.local",
        "father_first_name": "Gener",
        "father_last_name": "Magpantay",
        "father_phone": "0918-555-0129",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 16.5,
        "height": 101.2,
    },
    {
        "account_num": 30,
        "username": "parent030",
        "first_name": "Janine Bianca",
        "middle_initial": "U",
        "last_name": "Umali",
        "age": 3,
        "dob": "2021-02-14",
        "gender": "Female",
        "shift": "Morning",
        "street": "10 Jasmin St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Grace",
        "mother_last_name": "Umali",
        "mother_phone": "0917-555-0130",
        "mother_email": "grace.umali@bmv3.demo.local",
        "father_first_name": "Ariel",
        "father_last_name": "Umali",
        "father_phone": "0918-555-0130",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 13.6,
        "height": 92.8,
    },

    # ------------------ AFTERNOON SHIFT (30 Children) ------------------
    {
        "account_num": 31,
        "username": "parent031",
        "first_name": "Rafael Dominic",
        "middle_initial": "G",
        "last_name": "Guinto",
        "age": 4,
        "dob": "2020-04-19",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "23 Champaca St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Judith",
        "mother_last_name": "Guinto",
        "mother_phone": "0917-555-0131",
        "mother_email": "judith.guinto@bmv3.demo.local",
        "father_first_name": "Orlando",
        "father_last_name": "Guinto",
        "father_phone": "0918-555-0131",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.1,
        "height": 96.8,
    },
    {
        "account_num": 32,
        "username": "parent032",
        "first_name": "Nicole Stephanie",
        "middle_initial": "A",
        "last_name": "Aranda",
        "age": 4,
        "dob": "2020-06-12",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "15 Dalia St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Evelyn",
        "mother_last_name": "Aranda",
        "mother_phone": "0917-555-0132",
        "mother_email": "evelyn.aranda@bmv3.demo.local",
        "father_first_name": "Arthur",
        "father_last_name": "Aranda",
        "father_phone": "0918-555-0132",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.2,
        "height": 95.1,
    },
    {
        "account_num": 33,
        "username": "parent033",
        "first_name": "Carl Vincent",
        "middle_initial": "A",
        "last_name": "Alcantara",
        "age": 4,
        "dob": "2020-08-15",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "32 Ilang-Ilang St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Carmelita",
        "mother_last_name": "Alcantara",
        "mother_phone": "0917-555-0133",
        "mother_email": "carmelita.alcantara@bmv3.demo.local",
        "father_first_name": "Wilfredo",
        "father_last_name": "Alcantara",
        "father_phone": "0918-555-0133",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.7,
        "height": 96.4,
    },
    {
        "account_num": 34,
        "username": "parent034",
        "first_name": "Trisha May",
        "middle_initial": "M",
        "last_name": "Manalo",
        "age": 3,
        "dob": "2021-01-10",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "14 Rosal St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Melanie",
        "mother_last_name": "Manalo",
        "mother_phone": "0917-555-0134",
        "mother_email": "melanie.manalo@bmv3.demo.local",
        "father_first_name": "Roderick",
        "father_last_name": "Manalo",
        "father_phone": "0918-555-0134",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 13.5,
        "height": 92.6,
    },
    {
        "account_num": 35,
        "username": "parent035",
        "first_name": "Mark Kenneth",
        "middle_initial": "B",
        "last_name": "Beltran",
        "age": 5,
        "dob": "2019-10-15",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "41 Gumamela St.",
        "purok": "Purok 5",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Vilma",
        "mother_last_name": "Beltran",
        "mother_phone": "0917-555-0135",
        "mother_email": "vilma.beltran@bmv3.demo.local",
        "father_first_name": "Dominador",
        "father_last_name": "Beltran",
        "father_phone": "0918-555-0135",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 16.7,
        "height": 101.8,
    },
    {
        "account_num": 36,
        "username": "parent036",
        "first_name": "Angelica Faith",
        "middle_initial": "D",
        "last_name": "Dimaculangan",
        "age": 4,
        "dob": "2020-03-22",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "20 Ditas St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Nenita",
        "mother_last_name": "Dimaculangan",
        "mother_phone": "0917-555-0136",
        "mother_email": "nenita.dimaculangan@bmv3.demo.local",
        "father_first_name": "Ronnie",
        "father_last_name": "Dimaculangan",
        "father_phone": "0918-555-0136",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.4,
        "height": 95.5,
    },
    {
        "account_num": 37,
        "username": "parent037",
        "first_name": "Adrian James",
        "middle_initial": "E",
        "last_name": "Espiritu",
        "age": 4,
        "dob": "2020-07-11",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "29 Cattleya St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Lilian",
        "mother_last_name": "Espiritu",
        "mother_phone": "0917-555-0137",
        "mother_email": "lilian.espiritu@bmv3.demo.local",
        "father_first_name": "Jaime",
        "father_last_name": "Espiritu",
        "father_phone": "0918-555-0137",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.9,
        "height": 96.9,
    },
    {
        "account_num": 38,
        "username": "parent038",
        "first_name": "Catherine Joy",
        "middle_initial": "L",
        "last_name": "Legaspi",
        "age": 4,
        "dob": "2020-09-28",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "18 Waling-Waling St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Norma",
        "mother_last_name": "Legaspi",
        "mother_phone": "0917-555-0138",
        "mother_email": "norma.legaspi@bmv3.demo.local",
        "father_first_name": "Ernesto",
        "father_last_name": "Legaspi",
        "father_phone": "0918-555-0138",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.3,
        "height": 95.3,
    },
    {
        "account_num": 39,
        "username": "parent039",
        "first_name": "Miguel Angelo",
        "middle_initial": "Q",
        "last_name": "Quizon",
        "age": 4,
        "dob": "2020-02-04",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "36 Everlasting St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Cynthia",
        "mother_last_name": "Quizon",
        "mother_phone": "0917-555-0139",
        "mother_email": "cynthia.quizon@bmv3.demo.local",
        "father_first_name": "Mario",
        "father_last_name": "Quizon",
        "father_phone": "0918-555-0139",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.5,
        "height": 98.0,
    },
    {
        "account_num": 40,
        "username": "parent040",
        "first_name": "Christine Bernadette",
        "middle_initial": "P",
        "last_name": "Palma",
        "age": 3,
        "dob": "2021-04-18",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "12 Bougainvillea St.",
        "purok": "Purok 5",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Rowena",
        "mother_last_name": "Palma",
        "mother_phone": "0917-555-0140",
        "mother_email": "rowena.palma@bmv3.demo.local",
        "father_first_name": "Bernard",
        "father_last_name": "Palma",
        "father_phone": "0918-555-0140",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 13.8,
        "height": 93.4,
    },
    {
        "account_num": 41,
        "username": "parent041",
        "first_name": "Patrick Jerome",
        "middle_initial": "S",
        "last_name": "Serrano",
        "age": 4,
        "dob": "2020-11-25",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "26 Camia St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Gina",
        "mother_last_name": "Serrano",
        "mother_phone": "0917-555-0141",
        "mother_email": "gina.serrano@bmv3.demo.local",
        "father_first_name": "Patrick Sr.",
        "father_last_name": "Serrano",
        "father_phone": "0918-555-0141",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.8,
        "height": 96.3,
    },
    {
        "account_num": 42,
        "username": "parent042",
        "first_name": "Erica Mae",
        "middle_initial": "M",
        "last_name": "Malabanan",
        "age": 4,
        "dob": "2020-05-19",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "17 Santan St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Remedios",
        "mother_last_name": "Malabanan",
        "mother_phone": "0917-555-0142",
        "mother_email": "remedios.malabanan@bmv3.demo.local",
        "father_first_name": "Edilberto",
        "father_last_name": "Malabanan",
        "father_phone": "0918-555-0142",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.5,
        "height": 95.8,
    },
    {
        "account_num": 43,
        "username": "parent043",
        "first_name": "Angelo Gabriel",
        "middle_initial": "R",
        "last_name": "Rosales",
        "age": 4,
        "dob": "2020-12-14",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "34 Adelfa St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Maritess",
        "mother_last_name": "Rosales",
        "mother_phone": "0917-555-0143",
        "mother_email": "maritess.rosales@bmv3.demo.local",
        "father_first_name": "Gabriel",
        "father_last_name": "Rosales",
        "father_phone": "0918-555-0143",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.0,
        "height": 96.5,
    },
    {
        "account_num": 44,
        "username": "parent044",
        "first_name": "Marielle Sophia",
        "middle_initial": "M",
        "last_name": "Macalintal",
        "age": 5,
        "dob": "2019-09-20",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "19 Cadena de Amor St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Florinda",
        "mother_last_name": "Macalintal",
        "mother_phone": "0917-555-0144",
        "mother_email": "florinda.macalintal@bmv3.demo.local",
        "father_first_name": "Danilo",
        "father_last_name": "Macalintal",
        "father_phone": "0918-555-0144",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 16.3,
        "height": 101.4,
    },
    {
        "account_num": 45,
        "username": "parent045",
        "first_name": "Sean Patrick",
        "middle_initial": "A",
        "last_name": "Abad",
        "age": 3,
        "dob": "2021-03-30",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "22 Jasmin St.",
        "purok": "Purok 5",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Cheryl",
        "mother_last_name": "Abad",
        "mother_phone": "0917-555-0145",
        "mother_email": "cheryl.abad@bmv3.demo.local",
        "father_first_name": "Patricio",
        "father_last_name": "Abad",
        "father_phone": "0918-555-0145",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 13.7,
        "height": 93.1,
    },
    {
        "account_num": 46,
        "username": "parent046",
        "first_name": "Kristine Joy",
        "middle_initial": "C",
        "last_name": "Custodio",
        "age": 4,
        "dob": "2020-08-07",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "16 Champaca St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Rosanna",
        "mother_last_name": "Custodio",
        "mother_phone": "0917-555-0146",
        "mother_email": "rosanna.custodio@bmv3.demo.local",
        "father_first_name": "Melchor",
        "father_last_name": "Custodio",
        "father_phone": "0918-555-0146",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.6,
        "height": 96.0,
    },
    {
        "account_num": 47,
        "username": "parent047",
        "first_name": "Justin Timothy",
        "middle_initial": "D",
        "last_name": "De Castro",
        "age": 4,
        "dob": "2020-01-29",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "29 Dalia St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Imelda",
        "mother_last_name": "De Castro",
        "mother_phone": "0917-555-0147",
        "mother_email": "imelda.decastro@bmv3.demo.local",
        "father_first_name": "Timothy Sr.",
        "father_last_name": "De Castro",
        "father_phone": "0918-555-0147",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.4,
        "height": 97.8,
    },
    {
        "account_num": 48,
        "username": "parent048",
        "first_name": "Denise Nicole",
        "middle_initial": "G",
        "last_name": "Galicia",
        "age": 4,
        "dob": "2020-06-25",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "40 Ilang-Ilang St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Nancy",
        "mother_last_name": "Galicia",
        "mother_phone": "0917-555-0148",
        "mother_email": "nancy.galicia@bmv3.demo.local",
        "father_first_name": "Edwin",
        "father_last_name": "Galicia",
        "father_phone": "0918-555-0148",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.2,
        "height": 95.3,
    },
    {
        "account_num": 49,
        "username": "parent049",
        "first_name": "Kevin Andre",
        "middle_initial": "I",
        "last_name": "Ilao",
        "age": 4,
        "dob": "2020-10-09",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "11 Rosal St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Agnes",
        "mother_last_name": "Ilao",
        "mother_phone": "0917-555-0149",
        "mother_email": "agnes.ilao@bmv3.demo.local",
        "father_first_name": "Ferdie",
        "father_last_name": "Ilao",
        "father_phone": "0918-555-0149",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.9,
        "height": 96.7,
    },
    {
        "account_num": 50,
        "username": "parent050",
        "first_name": "Stephanie Claire",
        "middle_initial": "L",
        "last_name": "Laurel",
        "age": 4,
        "dob": "2020-04-28",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "25 Gumamela St.",
        "purok": "Purok 5",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Cielito",
        "mother_last_name": "Laurel",
        "mother_phone": "0917-555-0150",
        "mother_email": "cielito.laurel@bmv3.demo.local",
        "father_first_name": "Arsenio",
        "father_last_name": "Laurel",
        "father_phone": "0918-555-0150",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.5,
        "height": 95.6,
    },
    {
        "account_num": 51,
        "username": "parent051",
        "first_name": "Vince Edward",
        "middle_initial": "M",
        "last_name": "Marasigan",
        "age": 5,
        "dob": "2019-12-18",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "14 Ditas St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Fe",
        "mother_last_name": "Marasigan",
        "mother_phone": "0917-555-0151",
        "mother_email": "fe.marasigan@bmv3.demo.local",
        "father_first_name": "Teodoro",
        "father_last_name": "Marasigan",
        "father_phone": "0918-555-0151",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 16.4,
        "height": 101.6,
    },
    {
        "account_num": 52,
        "username": "parent052",
        "first_name": "Rochelle Anne",
        "middle_initial": "N",
        "last_name": "Natividad",
        "age": 3,
        "dob": "2021-02-08",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "33 Cattleya St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Milagros",
        "mother_last_name": "Natividad",
        "mother_phone": "0917-555-0152",
        "mother_email": "milagros.natividad@bmv3.demo.local",
        "father_first_name": "Alfonso",
        "father_last_name": "Natividad",
        "father_phone": "0918-555-0152",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 13.6,
        "height": 92.9,
    },
    {
        "account_num": 53,
        "username": "parent053",
        "first_name": "Paolo Miguel",
        "middle_initial": "O",
        "last_name": "Ordonez",
        "age": 4,
        "dob": "2020-07-03",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "21 Waling-Waling St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Zenaida",
        "mother_last_name": "Ordonez",
        "mother_phone": "0917-555-0153",
        "mother_email": "zenaida.ordonez@bmv3.demo.local",
        "father_first_name": "Conrado",
        "father_last_name": "Ordonez",
        "father_phone": "0918-555-0153",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.8,
        "height": 96.5,
    },
    {
        "account_num": 54,
        "username": "parent054",
        "first_name": "Camille Denise",
        "middle_initial": "P",
        "last_name": "Padilla",
        "age": 4,
        "dob": "2020-09-17",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "8 Everlasting St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Doris",
        "mother_last_name": "Padilla",
        "mother_phone": "0917-555-0154",
        "mother_email": "doris.padilla@bmv3.demo.local",
        "father_first_name": "Rico",
        "father_last_name": "Padilla",
        "father_phone": "0918-555-0154",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.4,
        "height": 95.4,
    },
    {
        "account_num": 55,
        "username": "parent055",
        "first_name": "Gerald Anthony",
        "middle_initial": "Q",
        "last_name": "Que",
        "age": 4,
        "dob": "2020-03-08",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "27 Bougainvillea St.",
        "purok": "Purok 5",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Wilma",
        "mother_last_name": "Que",
        "mother_phone": "0917-555-0155",
        "mother_email": "wilma.que@bmv3.demo.local",
        "father_first_name": "Henry",
        "father_last_name": "Que",
        "father_phone": "0918-555-0155",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.3,
        "height": 97.4,
    },
    {
        "account_num": 56,
        "username": "parent056",
        "first_name": "Hazel Joy",
        "middle_initial": "R",
        "last_name": "Remulla",
        "age": 4,
        "dob": "2020-11-02",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "16 Camia St.",
        "purok": "Purok 1",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Perla",
        "mother_last_name": "Remulla",
        "mother_phone": "0917-555-0156",
        "mother_email": "perla.remulla@bmv3.demo.local",
        "father_first_name": "Gaudencio",
        "father_last_name": "Remulla",
        "father_phone": "0918-555-0156",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.5,
        "height": 95.8,
    },
    {
        "account_num": 57,
        "username": "parent057",
        "first_name": "Dominic Francis",
        "middle_initial": "S",
        "last_name": "Samaniego",
        "age": 4,
        "dob": "2020-05-30",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "30 Santan St.",
        "purok": "Purok 2",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Vilma",
        "mother_last_name": "Samaniego",
        "mother_phone": "0917-555-0157",
        "mother_email": "vilma.samaniego@bmv3.demo.local",
        "father_first_name": "Rogelio",
        "father_last_name": "Samaniego",
        "father_phone": "0918-555-0157",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 15.0,
        "height": 96.6,
    },
    {
        "account_num": 58,
        "username": "parent058",
        "first_name": "Alyssa Marie",
        "middle_initial": "T",
        "last_name": "Tan",
        "age": 3,
        "dob": "2021-05-04",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "13 Adelfa St.",
        "purok": "Purok 3",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Grace",
        "mother_last_name": "Tan",
        "mother_phone": "0917-555-0158",
        "mother_email": "grace.tan@bmv3.demo.local",
        "father_first_name": "Wilson",
        "father_last_name": "Tan",
        "father_phone": "0918-555-0158",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 13.8,
        "height": 93.3,
    },
    {
        "account_num": 59,
        "username": "parent059",
        "first_name": "Zachary Kyle",
        "middle_initial": "V",
        "last_name": "Valencia",
        "age": 5,
        "dob": "2019-10-05",
        "gender": "Male",
        "shift": "Afternoon",
        "street": "22 Cadena de Amor St.",
        "purok": "Purok 4",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Maricel",
        "mother_last_name": "Valencia",
        "mother_phone": "0917-555-0159",
        "mother_email": "maricel.valencia@bmv3.demo.local",
        "father_first_name": "Edmundo",
        "father_last_name": "Valencia",
        "father_phone": "0918-555-0159",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 16.6,
        "height": 102.0,
    },
    {
        "account_num": 60,
        "username": "parent060",
        "first_name": "Zyra Monique",
        "middle_initial": "Y",
        "last_name": "Yambao",
        "age": 4,
        "dob": "2020-08-21",
        "gender": "Female",
        "shift": "Afternoon",
        "street": "19 Jasmin St.",
        "purok": "Purok 5",
        "barangay": "Market View",
        "city_municipality": "Lucena City",
        "mother_first_name": "Lorna",
        "mother_last_name": "Yambao",
        "mother_phone": "0917-555-0160",
        "mother_email": "lorna.yambao@bmv3.demo.local",
        "father_first_name": "Fidencio",
        "father_last_name": "Yambao",
        "father_phone": "0918-555-0160",
        "allergies": "None reported",
        "health_conditions": "None",
        "weight": 14.7,
        "height": 96.1,
    },
]

# Generate unique temporary passwords following a secure, memorable pattern per account
def generate_temp_password(account_num):
    # E.g. "Bmv3Demo#p001" - adheres to MinimumLengthValidator, mixes upper, lower, number, symbol
    return f"Bmv3Demo#p{account_num:03d}"


def get_or_create_school_years():
    """
    Ensures both the completed historical school year (2025-2026)
    and the current active school year (2026-2027) are configured.
    """
    # 1. Historical Year (2025-2026, Completed & Archived)
    hist_sy, created_hist = SchoolYear.objects.get_or_create(
        name="2025-2026",
        defaults={
            "is_active": False,
            "start_date": datetime.date(2025, 8, 25),
            "end_date": datetime.date(2026, 5, 29),
            "eccd_1st_start": datetime.date(2025, 9, 1),
            "eccd_1st_end": datetime.date(2025, 9, 26),
            "eccd_2nd_start": datetime.date(2026, 1, 5),
            "eccd_2nd_end": datetime.date(2026, 1, 30),
            "eccd_3rd_start": datetime.date(2026, 5, 4),
            "eccd_3rd_end": datetime.date(2026, 5, 29),
            "is_deleted": False,
        }
    )
    hist_sy.is_active = False
    hist_sy.start_date = datetime.date(2025, 8, 25)
    hist_sy.end_date = datetime.date(2026, 5, 29)
    hist_sy.eccd_1st_start = datetime.date(2025, 9, 1)
    hist_sy.eccd_1st_end = datetime.date(2025, 9, 26)
    hist_sy.eccd_2nd_start = datetime.date(2026, 1, 5)
    hist_sy.eccd_2nd_end = datetime.date(2026, 1, 30)
    hist_sy.eccd_3rd_start = datetime.date(2026, 5, 4)
    hist_sy.eccd_3rd_end = datetime.date(2026, 5, 29)
    hist_sy.is_deleted = False
    hist_sy.save()

    # 2. Current Active Year (2026-2027)
    active_sy, created_act = SchoolYear.objects.get_or_create(
        name="2026-2027",
        defaults={
            "is_active": True,
            "start_date": datetime.date(2026, 8, 24),
            "end_date": datetime.date(2027, 5, 28),
            "eccd_1st_start": datetime.date(2026, 9, 1),
            "eccd_1st_end": datetime.date(2026, 9, 25),
            "eccd_2nd_start": datetime.date(2027, 1, 4),
            "eccd_2nd_end": datetime.date(2027, 1, 29),
            "eccd_3rd_start": datetime.date(2027, 5, 3),
            "eccd_3rd_end": datetime.date(2027, 5, 28),
            "is_deleted": False,
        }
    )
    active_sy.is_active = True
    active_sy.is_deleted = False
    active_sy.save()

    # Safely migrate any children & records attached to rogue / accidental school years
    rogue_sys = SchoolYear.objects.exclude(id__in=[hist_sy.id, active_sy.id])
    for rogue in rogue_sys:
        Child.objects.filter(school_year=rogue).update(school_year=hist_sy)
        AttendanceRecord.objects.filter(school_year=rogue).update(school_year=hist_sy)
        NutritionRecord.objects.filter(school_year=rogue).update(school_year=hist_sy)
        ECCDAssessment.objects.filter(school_year=rogue).update(school_year=hist_sy)
        BMIRecord.objects.filter(school_year=rogue).update(school_year=hist_sy)
        EngagementRecord.objects.filter(school_year=rogue).update(school_year=hist_sy)
        Activity.objects.filter(school_year=rogue).update(school_year=hist_sy)
        NoClassDay.objects.filter(school_year=rogue).update(school_year=hist_sy)
    rogue_sys.delete()

    # Ensure strictly only 2026-2027 is active
    SchoolYear.objects.exclude(id=active_sy.id).update(is_active=False)

    return hist_sy, active_sy


@transaction.atomic
def reset_demonstration_database():
    """
    Safely purges only demonstration student and parent records.
    Preserves:
    - Teacher and Admin accounts (is_teacher=True or is_staff=True or is_superuser=True)
    - jeremy_960 parent account (current active parent of Sky Dylan)
    - Database schema & migrations
    - ECCD Domains and Milestones
    - CenterSettings
    """
    # 1. Identify non-teacher parent users
    teacher_users = User.objects.filter(userprofile__is_teacher=True)
    staff_users = User.objects.filter(is_staff=True)
    super_users = User.objects.filter(is_superuser=True)
    jeremy_user = User.objects.filter(username="jeremy_960")
    protected_user_ids = set(teacher_users.values_list('id', flat=True)) | \
                         set(staff_users.values_list('id', flat=True)) | \
                         set(super_users.values_list('id', flat=True)) | \
                         set(jeremy_user.values_list('id', flat=True))

    demo_parent_users = User.objects.exclude(id__in=protected_user_ids)
    demo_parent_count = demo_parent_users.count()
    child_count = Child.objects.count()

    # Delete dependent activity completions and activities from old test years
    StudentActivityCompletion.objects.all().delete()
    Activity.objects.filter(school_year__name__in=["1st BAtch", "2nd Batch", "2024-2025"]).delete()

    # Cascade delete all existing demo children (cascades to attendance, nutrition, milestones, assessments)
    Child.objects.all().delete()

    # Cascade delete demo parent accounts (cascades to UserProfile)
    demo_parent_users.delete()

    # Clean up any leftover test school years that are not 2025-2026 or 2026-2027
    SchoolYear.objects.filter(name__in=["1st BAtch", "2nd Batch", "2024-2025"]).delete()

    return {
        "deleted_children": child_count,
        "deleted_parents": demo_parent_count,
    }


@transaction.atomic
def seed_historical_school_year(progress_callback=None):
    """
    Creates and populates the historical school year 2025-2026 with:
    - 60 unique children (30 Morning Shift, 30 Afternoon Shift)
    - Complete guardian details for every child
    - Historical attendance spanning Sep 2025 - Apr 2026
    - Nutrition & BMI records across 3 quarters
    - Finalized ECCD evaluations & milestone scores across 7 domains
    - Historical behavior/engagement and activity records
    """
    hist_sy, active_sy = get_or_create_school_years()

    # Find teacher profile to assign as examiner
    teacher_profile = UserProfile.objects.filter(is_teacher=True).first()
    if not teacher_profile:
        # Fallback to superuser
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            teacher_profile, _ = UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={"is_teacher": True, "first_login": False}
            )

    # Pre-fetch ECCD milestones
    milestones = list(ECCDMilestone.objects.all().order_by('domain__order', 'order_number'))

    # Representative historical attendance dates (20 school days in 2025-2026)
    attendance_dates = [
        datetime.date(2025, 9, 1),  datetime.date(2025, 9, 8),  datetime.date(2025, 9, 15), datetime.date(2025, 9, 22),
        datetime.date(2025, 10, 6), datetime.date(2025, 10, 13), datetime.date(2025, 10, 20), datetime.date(2025, 10, 27),
        datetime.date(2025, 11, 3), datetime.date(2025, 11, 10), datetime.date(2025, 11, 17), datetime.date(2025, 11, 24),
        datetime.date(2025, 12, 1), datetime.date(2025, 12, 8),  datetime.date(2025, 12, 15),
        datetime.date(2026, 1, 12), datetime.date(2026, 1, 19), datetime.date(2026, 2, 9),
        datetime.date(2026, 3, 9), datetime.date(2026, 4, 6),
    ]

    absence_reasons = [
        "Fever and common cold",
        "Severe cough and throat irritation",
        "Inclement monsoon weather / heavy localized rain",
        "Family emergency and travel",
        "Mild stomach discomfort",
        "Scheduled pediatric dental visit",
    ]

    snack_notes_templates = [
        "Ate all of the warm champorado and drank fresh milk.",
        "Finished the boiled saba banana with great appetite.",
        "Ate entire pandesal with egg and shared happily with classmates.",
        "Finished arroz caldo with chicken and drank water.",
        "Ate half portion of lugaw and finished water bottle.",
        "Finished fresh sliced papaya and biscuits during morning snack.",
    ]

    created_children = []
    morning_count = 0
    afternoon_count = 0

    # 1. Create 6 Historical Activities for 2025-2026
    activities_data = [
        ("Buwan ng Wika Cultural Day", "Filipino cultural songs, traditional games, and costume presentation.", datetime.date(2025, 8, 29)),
        ("National Children's Month Art Fair", "Finger-painting and sensory art exhibit highlighting children's rights.", datetime.date(2025, 10, 24)),
        ("Handwashing & Health Hygiene Workshop", "Demonstration of proper handwashing steps and dental care.", datetime.date(2025, 11, 14)),
        ("BMV3 Daycare Christmas Program", "Holiday caroling, gift-giving, and festive dance presentations.", datetime.date(2025, 12, 18)),
        ("Community Helpers Day", "Interactive roleplaying as doctors, firemen, and teachers with barangay guests.", datetime.date(2026, 2, 20)),
        ("Moving-Up Ceremony & Recognition", "Recognition of achievements and moving-up ceremony for daycare graduates.", datetime.date(2026, 5, 27)),
    ]
    activities = []
    for name, desc, act_date in activities_data:
        act, _ = Activity.objects.get_or_create(
            name=name,
            school_year=hist_sy,
            defaults={"description": desc, "date": act_date}
        )
        activities.append(act)

    # 2. Populate 60 Children and their associated historical records
    for idx, p in enumerate(CHILDREN_PROFILES, 1):
        dob_date = datetime.datetime.strptime(p["dob"], "%Y-%m-%d").date()
        doe_date = datetime.date(2025, 8, random.choice([18, 19, 20, 21, 22]))

        child, created = Child.objects.get_or_create(
            first_name=p["first_name"],
            last_name=p["last_name"],
            school_year=hist_sy,
            defaults={
                "middle_initial": p["middle_initial"],
                "age": p["age"],
                "dob": dob_date,
                "doe": doe_date,
                "gender": p["gender"],
                "shift": p["shift"],
                "enrollment_status": "Enrolled",
                "attendance_status": "Present",
                "street": p["street"],
                "purok": p["purok"],
                "barangay": p["barangay"],
                "city_municipality": p["city_municipality"],
                "phone": p["mother_phone"],
                "email": p["mother_email"],
                "mother_first_name": p["mother_first_name"],
                "mother_middle_initial": "M",
                "mother_last_name": p["mother_last_name"],
                "mother_phone": p["mother_phone"],
                "mother_email": p["mother_email"],
                "mother_address": f"{p['street']}, {p['purok']}, {p['barangay']}, {p['city_municipality']}",
                "father_first_name": p["father_first_name"],
                "father_middle_initial": "F",
                "father_last_name": p["father_last_name"],
                "father_phone": p["father_phone"],
                "father_email": f"{p['father_first_name'].lower()}.{p['father_last_name'].lower()}@bmv3.demo.local",
                "father_address": f"{p['street']}, {p['purok']}, {p['barangay']}, {p['city_municipality']}",
                "allergies": p["allergies"],
                "health_conditions": p["health_conditions"],
                "weight": p["weight"],
                "height": p["height"],
            }
        )

        # Clear any parent links on historical archived pupils so parent demo accounts remain empty
        child.parents.clear()

        if p["shift"] == "Morning":
            morning_count += 1
        else:
            afternoon_count += 1

        created_children.append(child)

        # Activity Completions
        for act in activities:
            StudentActivityCompletion.objects.get_or_create(
                child=child,
                activity=act,
                defaults={"completed": True, "remarks": "Actively participated and enjoyed the event."}
            )

        # Milestone Checklist Record
        MilestoneRecord.objects.get_or_create(
            child=child,
            defaults={
                "tasks": {
                    "self_care": True,
                    "handwashing": True,
                    "color_recognition": True,
                    "counting_1_to_10": True,
                    "sharing_toys": True,
                    "following_instructions": True,
                }
            }
        )

        # Attendance Records (20 days)
        dropoff_str = "07:45 AM" if p["shift"] == "Morning" else "12:45 PM"
        for d in attendance_dates:
            roll = (idx * 7 + d.day * 13) % 100
            if roll < 84:
                status = "Present"
                reason = None
            elif roll < 94:
                status = "Absent"
                reason = absence_reasons[(idx + d.month) % len(absence_reasons)]
            else:
                status = "Late"
                reason = "Delayed due to morning traffic"

            AttendanceRecord.objects.get_or_create(
                child=child,
                date=d,
                session=p["shift"],
                defaults={
                    "school_year": hist_sy,
                    "status": status,
                    "absence_reason": reason,
                    "dropoff_time": dropoff_str if status != "Absent" else "",
                    "pickup_status": "Picked up on time" if status != "Absent" else "",
                    "authorized_guardian": f"{p['mother_first_name']} {p['mother_last_name']}",
                }
            )

        # Nutrition Records (Selected 8 days)
        for nut_date in attendance_dates[:8]:
            n_roll = (idx * 5 + nut_date.day * 7) % 10
            if n_roll < 7:
                snack_status = "Finished"
            elif n_roll < 9:
                snack_status = "Some Left"
            else:
                snack_status = "Not Eaten"

            NutritionRecord.objects.get_or_create(
                child=child,
                date=nut_date,
                defaults={
                    "school_year": hist_sy,
                    "snack_status": snack_status,
                    "teacher_notes": snack_notes_templates[(idx + nut_date.day) % len(snack_notes_templates)],
                }
            )

        # Engagement / Behavior Records (4 entries)
        behavior_entries = [
            (datetime.date(2025, 9, 19), "Positive", "Very cooperative during storytelling and group dance."),
            (datetime.date(2025, 11, 7), "Attentive", "Focused well during number identification games."),
            (datetime.date(2026, 1, 23), "Cooperative", "Helped tidy up toys and showed kindness to peers."),
            (datetime.date(2026, 3, 20), "Active", "Demonstrated high energy and cheerful participation in free play."),
        ]
        for b_date, b_status, b_notes in behavior_entries:
            EngagementRecord.objects.get_or_create(
                child=child,
                date=b_date,
                defaults={
                    "school_year": hist_sy,
                    "behavior": b_status,
                    "notes": b_notes,
                }
            )

        # BMI Records across 3 Quarters (Showing healthy growth)
        base_w = p["weight"]
        base_h = p["height"]
        bmi_data = [
            ("1st", base_w, base_h, datetime.date(2025, 9, 9)),
            ("2nd", round(base_w + 0.6, 1), round(base_h + 1.8, 1), datetime.date(2026, 1, 13)),
            ("3rd", round(base_w + 1.2, 1), round(base_h + 3.6, 1), datetime.date(2026, 5, 11)),
        ]
        for q_label, q_w, q_h, q_date in bmi_data:
            BMIRecord.objects.get_or_create(
                child=child,
                school_year=hist_sy,
                quarter=q_label,
                defaults={
                    "weight": q_w,
                    "height": q_h,
                    "measurement_date": q_date,
                    "status": "Finalized",
                }
            )

        # ECCD Assessments for 1st, 2nd, and 3rd Periods
        eccd_periods = [
            ("1st", datetime.date(2025, 9, 17), "Baseline assessment. Showing good adaptation to daycare routine.", "Friendly and eager to participate.", "Needs guidance with small motor tasks like scissors.", "Continue regular fine motor activities."),
            ("2nd", datetime.date(2026, 1, 19), "Mid-year assessment. Marked progress observed in language and self-help.", "Communicates needs clearly and shares toys willingly.", "Improving counting confidence.", "Reinforce number concepts at home."),
            ("3rd", datetime.date(2026, 5, 18), "Final year evaluation. Child is well-prepared for kindergarten transition.", "Consistently demonstrates self-reliance, social harmony, and cognitive curiosity.", "None. Readiness milestones successfully met.", "Maintain reading and storytelling habits."),
        ]

        for p_label, a_date, rem, stren, conc, f_up in eccd_periods:
            assessment, _ = ECCDAssessment.objects.get_or_create(
                child=child,
                school_year=hist_sy,
                assessment_period=p_label,
                defaults={
                    "teacher": teacher_profile,
                    "assessment_date": a_date,
                    "status": "Finalized",
                    "remarks": rem,
                    "strengths": stren,
                    "concerns": conc,
                    "follow_up_action": f_up,
                }
            )

            scores_to_create = []
            for m in milestones:
                m_hash = (idx * 31 + m.id * 17) % 100
                if p_label == "1st":
                    score = 2 if m_hash < 25 else (1 if m_hash < 80 else 0)
                elif p_label == "2nd":
                    score = 2 if m_hash < 65 else (1 if m_hash < 95 else 0)
                else:  # 3rd period
                    score = 2 if m_hash < 90 else 1

                scores_to_create.append(
                    ECCDMilestoneScore(
                        assessment=assessment,
                        milestone=m,
                        teacher_score=score,
                        parent_score=score,
                        teacher_observation=f"Demonstrated appropriately during {p_label} evaluation.",
                    )
                )

            ECCDMilestoneScore.objects.bulk_create(scores_to_create, ignore_conflicts=True)

        if progress_callback:
            progress_callback(idx, len(CHILDREN_PROFILES))

    return {
        "historical_school_year": hist_sy.name,
        "total_children": len(created_children),
        "morning_count": morning_count,
        "afternoon_count": afternoon_count,
    }


@transaction.atomic
def seed_demo_parent_accounts(reset_passwords=False):
    """
    Provisions exactly 80 built-in demonstration parent accounts (parent001 to parent080)
    with NO enrolled children and mandatory first-login password change.
    These accounts are purely blank and ready for new enrollments in the current school year (2026-2027).
    """
    csv_rows = []
    created_count = 0
    updated_count = 0

    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    csv_paths = [
        base_dir / "bmv3_80_demo_parent_credentials.csv",
        base_dir / "bmv3_demo_parent_credentials.csv",
    ]

    for i in range(1, 81):
        acc_num = f"{i:03d}"
        username = f"parent{acc_num}"
        temp_password = f"Bmv3!Parent{acc_num}#"
        email = f"parent{acc_num}@demo.bmv3.local"
        parent_name = f"Parent Demo{acc_num}"

        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": "Parent",
                "last_name": "",
                "is_staff": False,
                "is_superuser": False,
            }
        )

        user.set_password(temp_password)
        user.email = email
        user.first_name = "Parent"
        user.last_name = ""
        user.is_active = True
        user.save()

        profile, prof_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "is_teacher": False,
                "first_login": True,
                "is_account_restricted": False,
                "home_address_text": f"Lucena City Demonstration Zone {acc_num}",
            }
        )

        profile.first_login = True
        profile.is_account_restricted = False
        profile.save()

        # Ensure NO children are attached - pure empty parent accounts ready for enrollment
        profile.children.clear()

        if user_created:
            created_count += 1
        else:
            updated_count += 1

        csv_rows.append({
            "Account": i,
            "Username": username,
            "Temporary Password": temp_password,
            "Parent / Guardian Name": parent_name,
            "Assigned Pupil": "None (Ready for Enrollment)",
            "Shift": "Unassigned",
            "First Login Password Change": "Required" if profile.first_login else "Completed",
        })

    for cp in csv_paths:
        try:
            with open(cp, mode="w", newline="", encoding="utf-8") as f:
                fieldnames = [
                    "Account", "Username", "Temporary Password",
                    "Parent / Guardian Name", "Assigned Pupil",
                    "Shift", "First Login Password Change"
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_rows)
        except Exception:
            pass

    return {
        "total_accounts": len(csv_rows),
        "created_count": created_count,
        "updated_count": updated_count,
        "csv_path": str(csv_paths[0]),
        "accounts": csv_rows,
    }

