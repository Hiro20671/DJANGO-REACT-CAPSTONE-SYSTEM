import os
import csv
import random
import datetime
from decimal import Decimal
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings
from apps.core.models import (
    SchoolYear, Child, UserProfile, AttendanceRecord,
    NutritionRecord, BMIRecord, ECCDAssessment, ECCDMilestone,
    ECCDMilestoneScore, MilestoneRecord, ECCDBookletRecord,
    Activity, StudentActivityCompletion, Announcement,
    ProgramHighlight, EnrollmentInfo, CenterSettings, NoClassDay
)

# 80 Distinct, Realistic Filipino Daycare Pupils (40 Morning, 40 Afternoon)
# Directly assigned to parent001 through parent080
ACTIVE_CHILDREN_PROFILES = [
    # ========================== MORNING SHIFT (40 Pupils: parent001 - parent040) ==========================
    {
        "account_num": 1, "username": "parent001", "first_name": "Juan Gabriel", "middle_initial": "S", "last_name": "Santos",
        "age": 4, "dob": "2022-04-12", "gender": "Male", "shift": "Morning",
        "street": "14 Sampaguita St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Elena", "mother_last_name": "Santos", "mother_phone": "0917-555-0101", "mother_email": "elena.santos@bmv3.demo.local",
        "father_first_name": "Roberto", "father_last_name": "Santos", "father_phone": "0918-555-0101",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.8, "height": 96.5,
    },
    {
        "account_num": 2, "username": "parent002", "first_name": "Maria Angela", "middle_initial": "R", "last_name": "Reyes",
        "age": 4, "dob": "2022-07-25", "gender": "Female", "shift": "Morning",
        "street": "28 Rosal St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Corazon", "mother_last_name": "Reyes", "mother_phone": "0917-555-0102", "mother_email": "corazon.reyes@bmv3.demo.local",
        "father_first_name": "Danilo", "father_last_name": "Reyes", "father_phone": "0918-555-0102",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.2, "height": 95.0,
    },
    {
        "account_num": 3, "username": "parent003", "first_name": "Mateo Luis", "middle_initial": "C", "last_name": "Cruz",
        "age": 4, "dob": "2022-02-18", "gender": "Male", "shift": "Morning",
        "street": "5 Ilang-Ilang St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Lourdes", "mother_last_name": "Cruz", "mother_phone": "0917-555-0103", "mother_email": "lourdes.cruz@bmv3.demo.local",
        "father_first_name": "Eduardo", "father_last_name": "Cruz", "father_phone": "0918-555-0103",
        "allergies": "Peanuts", "health_conditions": "Mild Allergic Rhinitis", "weight": 15.6, "height": 98.2,
    },
    {
        "account_num": 4, "username": "parent004", "first_name": "Sofia Beatrice", "middle_initial": "G", "last_name": "Garcia",
        "age": 3, "dob": "2023-03-09", "gender": "Female", "shift": "Morning",
        "street": "42 Gumamela St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Rowena", "mother_last_name": "Garcia", "mother_phone": "0917-555-0104", "mother_email": "rowena.garcia@bmv3.demo.local",
        "father_first_name": "Ferdinand", "father_last_name": "Garcia", "father_phone": "0918-555-0104",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.5, "height": 92.4,
    },
    {
        "account_num": 5, "username": "parent005", "first_name": "Lucas Antonio", "middle_initial": "B", "last_name": "Bautista",
        "age": 4, "dob": "2022-09-14", "gender": "Male", "shift": "Morning",
        "street": "19 Ditas St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Maricel", "mother_last_name": "Bautista", "mother_phone": "0917-555-0105", "mother_email": "maricel.bautista@bmv3.demo.local",
        "father_first_name": "Arnel", "father_last_name": "Bautista", "father_phone": "0918-555-0105",
        "allergies": "Dust mite sensitivity", "health_conditions": "Asthma (Mild)", "weight": 14.5, "height": 96.0,
    },
    {
        "account_num": 6, "username": "parent006", "first_name": "Althea Mae", "middle_initial": "M", "last_name": "Mendoza",
        "age": 4, "dob": "2022-06-30", "gender": "Female", "shift": "Morning",
        "street": "8 Cattleya St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Jennifer", "mother_last_name": "Mendoza", "mother_phone": "0917-555-0106", "mother_email": "jennifer.mendoza@bmv3.demo.local",
        "father_first_name": "Noel", "father_last_name": "Mendoza", "father_phone": "0918-555-0106",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.0, "height": 94.8,
    },
    {
        "account_num": 7, "username": "parent007", "first_name": "Gabriel Miguel", "middle_initial": "R", "last_name": "Ramos",
        "age": 4, "dob": "2021-11-22", "gender": "Male", "shift": "Morning",
        "street": "33 Waling-Waling St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Carmela", "mother_last_name": "Ramos", "mother_phone": "0917-555-0107", "mother_email": "carmela.ramos@bmv3.demo.local",
        "father_first_name": "Mark Anthony", "father_last_name": "Ramos", "father_phone": "0918-555-0107",
        "allergies": "None reported", "health_conditions": "None", "weight": 16.2, "height": 99.5,
    },
    {
        "account_num": 8, "username": "parent008", "first_name": "Samantha Nicole", "middle_initial": "D", "last_name": "Dela Cruz",
        "age": 4, "dob": "2022-05-19", "gender": "Female", "shift": "Morning",
        "street": "12 Dahlia St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Maria Fe", "mother_last_name": "Dela Cruz", "mother_phone": "0917-555-0108", "mother_email": "mariafe.delacruz@bmv3.demo.local",
        "father_first_name": "Reynaldo", "father_last_name": "Dela Cruz", "father_phone": "0918-555-0108",
        "allergies": "Chicken eggs (mild hives)", "health_conditions": "None", "weight": 14.1, "height": 95.2,
    },
    {
        "account_num": 9, "username": "parent009", "first_name": "Ethan James", "middle_initial": "F", "last_name": "Flores",
        "age": 3, "dob": "2023-01-14", "gender": "Male", "shift": "Morning",
        "street": "21 Jasmin St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Glenda", "mother_last_name": "Flores", "mother_phone": "0917-555-0109", "mother_email": "glenda.flores@bmv3.demo.local",
        "father_first_name": "Joseph", "father_last_name": "Flores", "father_phone": "0918-555-0109",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.8, "height": 93.6,
    },
    {
        "account_num": 10, "username": "parent010", "first_name": "Chloe Danielle", "middle_initial": "A", "last_name": "Aquino",
        "age": 4, "dob": "2022-08-03", "gender": "Female", "shift": "Morning",
        "street": "16 Everlasting St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Diana", "mother_last_name": "Aquino", "mother_phone": "0917-555-0110", "mother_email": "diana.aquino@bmv3.demo.local",
        "father_first_name": "Christopher", "father_last_name": "Aquino", "father_phone": "0918-555-0110",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.4, "height": 95.8,
    },
    {
        "account_num": 11, "username": "parent011", "first_name": "Elijah Paul", "middle_initial": "C", "last_name": "Castillo",
        "age": 4, "dob": "2022-03-27", "gender": "Male", "shift": "Morning",
        "street": "9 Bougainvillea St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Lilian", "mother_last_name": "Castillo", "mother_phone": "0917-555-0111", "mother_email": "lilian.castillo@bmv3.demo.local",
        "father_first_name": "Ramon", "father_last_name": "Castillo", "father_phone": "0918-555-0111",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.0, "height": 97.0,
    },
    {
        "account_num": 12, "username": "parent012", "first_name": "Princess Jasmine", "middle_initial": "V", "last_name": "Villanueva",
        "age": 4, "dob": "2022-10-11", "gender": "Female", "shift": "Morning",
        "street": "30 Daisy St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Joy", "mother_last_name": "Villanueva", "mother_phone": "0917-555-0112", "mother_email": "joy.villanueva@bmv3.demo.local",
        "father_first_name": "Christian", "father_last_name": "Villanueva", "father_phone": "0918-555-0112",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.3, "height": 95.5,
    },
    {
        "account_num": 13, "username": "parent013", "first_name": "Noah Alexander", "middle_initial": "O", "last_name": "Ocampo",
        "age": 4, "dob": "2022-04-05", "gender": "Male", "shift": "Morning",
        "street": "7 Lotus St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Teresa", "mother_last_name": "Ocampo", "mother_phone": "0917-555-0113", "mother_email": "teresa.ocampo@bmv3.demo.local",
        "father_first_name": "Gilbert", "father_last_name": "Ocampo", "father_phone": "0918-555-0113",
        "allergies": "Shellfish", "health_conditions": "None", "weight": 15.3, "height": 97.8,
    },
    {
        "account_num": 14, "username": "parent014", "first_name": "Hannah Sophia", "middle_initial": "D", "last_name": "David",
        "age": 3, "dob": "2023-02-20", "gender": "Female", "shift": "Morning",
        "street": "24 Camia St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Rosalie", "mother_last_name": "David", "mother_phone": "0917-555-0114", "mother_email": "rosalie.david@bmv3.demo.local",
        "father_first_name": "Patrick", "father_last_name": "David", "father_phone": "0918-555-0114",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.6, "height": 92.8,
    },
    {
        "account_num": 15, "username": "parent015", "first_name": "Daniel Joseph", "middle_initial": "R", "last_name": "Rivera",
        "age": 4, "dob": "2022-07-08", "gender": "Male", "shift": "Morning",
        "street": "18 Gardenia St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Evelyn", "mother_last_name": "Rivera", "mother_phone": "0917-555-0115", "mother_email": "evelyn.rivera@bmv3.demo.local",
        "father_first_name": "Jonathan", "father_last_name": "Rivera", "father_phone": "0918-555-0115",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.9, "height": 96.8,
    },
    {
        "account_num": 16, "username": "parent016", "first_name": "Andrea Camille", "middle_initial": "G", "last_name": "Gonzales",
        "age": 4, "dob": "2022-09-29", "gender": "Female", "shift": "Morning",
        "street": "11 Zinnia St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Christine", "mother_last_name": "Gonzales", "mother_phone": "0917-555-0116", "mother_email": "christine.gonzales@bmv3.demo.local",
        "father_first_name": "Dennis", "father_last_name": "Gonzales", "father_phone": "0918-555-0116",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.1, "height": 95.1,
    },
    {
        "account_num": 17, "username": "parent017", "first_name": "Caleb Joshua", "middle_initial": "S", "last_name": "Soriano",
        "age": 4, "dob": "2022-05-12", "gender": "Male", "shift": "Morning",
        "street": "26 Marigold St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Bernadette", "mother_last_name": "Soriano", "mother_phone": "0917-555-0117", "mother_email": "bernadette.soriano@bmv3.demo.local",
        "father_first_name": "Allan", "father_last_name": "Soriano", "father_phone": "0918-555-0117",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.2, "height": 97.4,
    },
    {
        "account_num": 18, "username": "parent018", "first_name": "Beatrix Reign", "middle_initial": "P", "last_name": "Pascual",
        "age": 3, "dob": "2023-03-25", "gender": "Female", "shift": "Morning",
        "street": "4 Magnolia St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Katrina", "mother_last_name": "Pascual", "mother_phone": "0917-555-0118", "mother_email": "katrina.pascual@bmv3.demo.local",
        "father_first_name": "Paolo", "father_last_name": "Pascual", "father_phone": "0918-555-0118",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.4, "height": 92.1,
    },
    {
        "account_num": 19, "username": "parent019", "first_name": "Sebastian Luke", "middle_initial": "T", "last_name": "Tolentino",
        "age": 4, "dob": "2022-01-30", "gender": "Male", "shift": "Morning",
        "street": "37 Azucena St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Melanie", "mother_last_name": "Tolentino", "mother_phone": "0917-555-0119", "mother_email": "melanie.tolentino@bmv3.demo.local",
        "father_first_name": "Eric", "father_last_name": "Tolentino", "father_phone": "0918-555-0119",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.8, "height": 98.6,
    },
    {
        "account_num": 20, "username": "parent020", "first_name": "Mikaela Joy", "middle_initial": "M", "last_name": "Medina",
        "age": 4, "dob": "2022-08-16", "gender": "Female", "shift": "Morning",
        "street": "15 Begonia St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Abigail", "mother_last_name": "Medina", "mother_phone": "0917-555-0120", "mother_email": "abigail.medina@bmv3.demo.local",
        "father_first_name": "Francis", "father_last_name": "Medina", "father_phone": "0918-555-0120",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.3, "height": 95.6,
    },
    {
        "account_num": 21, "username": "parent021", "first_name": "Asher Vance", "middle_initial": "M", "last_name": "Mercado",
        "age": 4, "dob": "2022-06-11", "gender": "Male", "shift": "Morning",
        "street": "22 Sunflower St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Sheryl", "mother_last_name": "Mercado", "mother_phone": "0917-555-0121", "mother_email": "sheryl.mercado@bmv3.demo.local",
        "father_first_name": "Angelo", "father_last_name": "Mercado", "father_phone": "0918-555-0121",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.7, "height": 96.3,
    },
    {
        "account_num": 22, "username": "parent022", "first_name": "Cassandra Gail", "middle_initial": "S", "last_name": "Salvador",
        "age": 4, "dob": "2022-11-04", "gender": "Female", "shift": "Morning",
        "street": "3 Carnation St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Giselle", "mother_last_name": "Salvador", "mother_phone": "0917-555-0122", "mother_email": "giselle.salvador@bmv3.demo.local",
        "father_first_name": "Victor", "father_last_name": "Salvador", "father_phone": "0918-555-0122",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.9, "height": 94.4,
    },
    {
        "account_num": 23, "username": "parent023", "first_name": "Nathan Ezekiel", "middle_initial": "V", "last_name": "Valenzuela",
        "age": 4, "dob": "2022-04-21", "gender": "Male", "shift": "Morning",
        "street": "29 Hyacinth St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Lorena", "mother_last_name": "Valenzuela", "mother_phone": "0917-555-0123", "mother_email": "lorena.valenzuela@bmv3.demo.local",
        "father_first_name": "Julius", "father_last_name": "Valenzuela", "father_phone": "0918-555-0123",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.1, "height": 97.2,
    },
    {
        "account_num": 24, "username": "parent024", "first_name": "Ysabella Rose", "middle_initial": "E", "last_name": "Espiritu",
        "age": 3, "dob": "2023-02-02", "gender": "Female", "shift": "Morning",
        "street": "10 Violeta St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Ma. Theresa", "mother_last_name": "Espiritu", "mother_phone": "0917-555-0124", "mother_email": "theresa.espiritu@bmv3.demo.local",
        "father_first_name": "Roderick", "father_last_name": "Espiritu", "father_phone": "0918-555-0124",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.7, "height": 93.2,
    },
    {
        "account_num": 25, "username": "parent025", "first_name": "Isaiah Thomas", "middle_initial": "C", "last_name": "Corpuz",
        "age": 4, "dob": "2022-07-17", "gender": "Male", "shift": "Morning",
        "street": "17 Verbena St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Annalyn", "mother_last_name": "Corpuz", "mother_phone": "0917-555-0125", "mother_email": "annalyn.corpuz@bmv3.demo.local",
        "father_first_name": "Darwin", "father_last_name": "Corpuz", "father_phone": "0918-555-0125",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.4, "height": 97.9,
    },
    {
        "account_num": 26, "username": "parent026", "first_name": "Angelica Faith", "middle_initial": "M", "last_name": "Manalo",
        "age": 4, "dob": "2022-10-28", "gender": "Female", "shift": "Morning",
        "street": "31 Petunia St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Rhea", "mother_last_name": "Manalo", "mother_phone": "0917-555-0126", "mother_email": "rhea.manalo@bmv3.demo.local",
        "father_first_name": "Alexander", "father_last_name": "Manalo", "father_phone": "0918-555-0126",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.0, "height": 95.0,
    },
    {
        "account_num": 27, "username": "parent027", "first_name": "Jacob Matthew", "middle_initial": "P", "last_name": "Pineda",
        "age": 4, "dob": "2022-03-14", "gender": "Male", "shift": "Morning",
        "street": "6 Tulip St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Geraldine", "mother_last_name": "Pineda", "mother_phone": "0917-555-0127", "mother_email": "geraldine.pineda@bmv3.demo.local",
        "father_first_name": "Jeffrey", "father_last_name": "Pineda", "father_phone": "0918-555-0127",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.6, "height": 96.2,
    },
    {
        "account_num": 28, "username": "parent028", "first_name": "Stephanie Claire", "middle_initial": "D", "last_name": "De Leon",
        "age": 3, "dob": "2023-01-29", "gender": "Female", "shift": "Morning",
        "street": "23 Aster St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Shirley", "mother_last_name": "De Leon", "mother_phone": "0917-555-0128", "mother_email": "shirley.deleon@bmv3.demo.local",
        "father_first_name": "Eugene", "father_last_name": "De Leon", "father_phone": "0918-555-0128",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.8, "height": 93.4,
    },
    {
        "account_num": 29, "username": "parent029", "first_name": "Zachary Keith", "middle_initial": "G", "last_name": "Guinto",
        "age": 4, "dob": "2022-08-22", "gender": "Male", "shift": "Morning",
        "street": "35 Lily St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Clarissa", "mother_last_name": "Guinto", "mother_phone": "0917-555-0129", "mother_email": "clarissa.guinto@bmv3.demo.local",
        "father_first_name": "Marvin", "father_last_name": "Guinto", "father_phone": "0918-555-0129",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.8, "height": 96.7,
    },
    {
        "account_num": 30, "username": "parent030", "first_name": "Alyssa Marie", "middle_initial": "B", "last_name": "Beltran",
        "age": 4, "dob": "2022-05-07", "gender": "Female", "shift": "Morning",
        "street": "13 Gladiola St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Joan", "mother_last_name": "Beltran", "mother_phone": "0917-555-0130", "mother_email": "joan.beltran@bmv3.demo.local",
        "father_first_name": "Oliver", "father_last_name": "Beltran", "father_phone": "0918-555-0130",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.2, "height": 95.3,
    },
    {
        "account_num": 31, "username": "parent031", "first_name": "Tristan Kyle", "middle_initial": "M", "last_name": "Magno",
        "age": 4, "dob": "2022-02-14", "gender": "Male", "shift": "Morning",
        "street": "18 Ilang-Ilang St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Gemma", "mother_last_name": "Magno", "mother_phone": "0917-555-0131", "mother_email": "gemma.magno@bmv3.demo.local",
        "father_first_name": "Gary", "father_last_name": "Magno", "father_phone": "0918-555-0131",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.5, "height": 98.0,
    },
    {
        "account_num": 32, "username": "parent032", "first_name": "Gianna Louise", "middle_initial": "C", "last_name": "Custodio",
        "age": 3, "dob": "2023-04-10", "gender": "Female", "shift": "Morning",
        "street": "25 Rosal St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Leah", "mother_last_name": "Custodio", "mother_phone": "0917-555-0132", "mother_email": "leah.custodio@bmv3.demo.local",
        "father_first_name": "Nestor", "father_last_name": "Custodio", "father_phone": "0918-555-0132",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.5, "height": 92.5,
    },
    {
        "account_num": 33, "username": "parent033", "first_name": "Dominic Rafael", "middle_initial": "T", "last_name": "Tan",
        "age": 4, "dob": "2022-06-25", "gender": "Male", "shift": "Morning",
        "street": "11 Dahlia St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Sherry", "mother_last_name": "Tan", "mother_phone": "0917-555-0133", "mother_email": "sherry.tan@bmv3.demo.local",
        "father_first_name": "Dominador", "father_last_name": "Tan", "father_phone": "0918-555-0133",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.8, "height": 96.6,
    },
    {
        "account_num": 34, "username": "parent034", "first_name": "Fiona Isabel", "middle_initial": "S", "last_name": "Serrano",
        "age": 4, "dob": "2022-09-08", "gender": "Female", "shift": "Morning",
        "street": "30 Gumamela St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Irene", "mother_last_name": "Serrano", "mother_phone": "0917-555-0134", "mother_email": "irene.serrano@bmv3.demo.local",
        "father_first_name": "Michael", "father_last_name": "Serrano", "father_phone": "0918-555-0134",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.2, "height": 95.2,
    },
    {
        "account_num": 35, "username": "parent035", "first_name": "Joaquin Marcus", "middle_initial": "I", "last_name": "Imperial",
        "age": 4, "dob": "2022-03-01", "gender": "Male", "shift": "Morning",
        "street": "7 Cattleya St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Grace", "mother_last_name": "Imperial", "mother_phone": "0917-555-0135", "mother_email": "grace.imperial@bmv3.demo.local",
        "father_first_name": "Jose", "father_last_name": "Imperial", "father_phone": "0918-555-0135",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.3, "height": 97.5,
    },
    {
        "account_num": 36, "username": "parent036", "first_name": "Chelsea Anne", "middle_initial": "R", "last_name": "Robles",
        "age": 4, "dob": "2022-07-19", "gender": "Female", "shift": "Morning",
        "street": "14 Ditas St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Hazel", "mother_last_name": "Robles", "mother_phone": "0917-555-0136", "mother_email": "hazel.robles@bmv3.demo.local",
        "father_first_name": "Renato", "father_last_name": "Robles", "father_phone": "0918-555-0136",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.0, "height": 94.9,
    },
    {
        "account_num": 37, "username": "parent037", "first_name": "Benjamin Seth", "middle_initial": "L", "last_name": "Legaspi",
        "age": 4, "dob": "2022-04-29", "gender": "Male", "shift": "Morning",
        "street": "21 Jasmin St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Lorna", "mother_last_name": "Legaspi", "mother_phone": "0917-555-0137", "mother_email": "lorna.legaspi@bmv3.demo.local",
        "father_first_name": "Benito", "father_last_name": "Legaspi", "father_phone": "0918-555-0137",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.1, "height": 97.1,
    },
    {
        "account_num": 38, "username": "parent038", "first_name": "Natalia Grace", "middle_initial": "V", "last_name": "Villar",
        "age": 3, "dob": "2023-02-15", "gender": "Female", "shift": "Morning",
        "street": "9 Sampaguita St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Daphne", "mother_last_name": "Villar", "mother_phone": "0917-555-0138", "mother_email": "daphne.villar@bmv3.demo.local",
        "father_first_name": "Nelson", "father_last_name": "Villar", "father_phone": "0918-555-0138",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.6, "height": 93.0,
    },
    {
        "account_num": 39, "username": "parent039", "first_name": "Carlos Miguel", "middle_initial": "A", "last_name": "Alcantara",
        "age": 4, "dob": "2022-08-11", "gender": "Male", "shift": "Morning",
        "street": "33 Waling-Waling St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Rosanna", "mother_last_name": "Alcantara", "mother_phone": "0917-555-0139", "mother_email": "rosanna.alcantara@bmv3.demo.local",
        "father_first_name": "Carlito", "father_last_name": "Alcantara", "father_phone": "0918-555-0139",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.7, "height": 96.4,
    },
    {
        "account_num": 40, "username": "parent040", "first_name": "Denise Nicole", "middle_initial": "E", "last_name": "Esguerra",
        "age": 4, "dob": "2022-05-23", "gender": "Female", "shift": "Morning",
        "street": "16 Lotus St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Eileen", "mother_last_name": "Esguerra", "mother_phone": "0917-555-0140", "mother_email": "eileen.esguerra@bmv3.demo.local",
        "father_first_name": "Edgar", "father_last_name": "Esguerra", "father_phone": "0918-555-0140",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.1, "height": 95.4,
    },

    # ========================== AFTERNOON SHIFT (40 Pupils: parent041 - parent080) ==========================
    {
        "account_num": 41, "username": "parent041", "first_name": "Marcus David", "middle_initial": "F", "last_name": "Fernandez",
        "age": 4, "dob": "2022-03-17", "gender": "Male", "shift": "Afternoon",
        "street": "5 Rosal St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Regina", "mother_last_name": "Fernandez", "mother_phone": "0917-555-0141", "mother_email": "regina.fernandez@bmv3.demo.local",
        "father_first_name": "Danilo", "father_last_name": "Fernandez", "father_phone": "0918-555-0141",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.4, "height": 97.7,
    },
    {
        "account_num": 42, "username": "parent042", "first_name": "Nicole Jane", "middle_initial": "L", "last_name": "Lopez",
        "age": 4, "dob": "2022-06-08", "gender": "Female", "shift": "Afternoon",
        "street": "22 Camia St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Janice", "mother_last_name": "Lopez", "mother_phone": "0917-555-0142", "mother_email": "janice.lopez@bmv3.demo.local",
        "father_first_name": "Ramil", "father_last_name": "Lopez", "father_phone": "0918-555-0142",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.0, "height": 94.8,
    },
    {
        "account_num": 43, "username": "parent043", "first_name": "Joaquin Rafael", "middle_initial": "P", "last_name": "Perez",
        "age": 4, "dob": "2022-09-21", "gender": "Male", "shift": "Afternoon",
        "street": "14 Gumamela St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Patricia", "mother_last_name": "Perez", "mother_phone": "0917-555-0143", "mother_email": "patricia.perez@bmv3.demo.local",
        "father_first_name": "Rolando", "father_last_name": "Perez", "father_phone": "0918-555-0143",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.8, "height": 96.5,
    },
    {
        "account_num": 44, "username": "parent044", "first_name": "Isabella Marie", "middle_initial": "M", "last_name": "Morales",
        "age": 3, "dob": "2023-01-11", "gender": "Female", "shift": "Afternoon",
        "street": "29 Ilang-Ilang St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Maricel", "mother_last_name": "Morales", "mother_phone": "0917-555-0144", "mother_email": "maricel.morales@bmv3.demo.local",
        "father_first_name": "Gerardo", "father_last_name": "Morales", "father_phone": "0918-555-0144",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.7, "height": 93.1,
    },
    {
        "account_num": 45, "username": "parent045", "first_name": "Christian Dave", "middle_initial": "N", "last_name": "Navarro",
        "age": 4, "dob": "2022-04-03", "gender": "Male", "shift": "Afternoon",
        "street": "8 Dahlia St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Divina", "mother_last_name": "Navarro", "mother_phone": "0917-555-0145", "mother_email": "divina.navarro@bmv3.demo.local",
        "father_first_name": "Cesar", "father_last_name": "Navarro", "father_phone": "0918-555-0145",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.2, "height": 97.3,
    },
    {
        "account_num": 46, "username": "parent046", "first_name": "Bea Clarisse", "middle_initial": "C", "last_name": "Cortez",
        "age": 4, "dob": "2022-08-14", "gender": "Female", "shift": "Afternoon",
        "street": "17 Sampaguita St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Cecilia", "mother_last_name": "Cortez", "mother_phone": "0917-555-0146", "mother_email": "cecilia.cortez@bmv3.demo.local",
        "father_first_name": "Arman", "father_last_name": "Cortez", "father_phone": "0918-555-0146",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.1, "height": 95.2,
    },
    {
        "account_num": 47, "username": "parent047", "first_name": "Ezekiel John", "middle_initial": "M", "last_name": "Miranda",
        "age": 4, "dob": "2022-05-18", "gender": "Male", "shift": "Afternoon",
        "street": "24 Cattleya St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Judith", "mother_last_name": "Miranda", "mother_phone": "0917-555-0147", "mother_email": "judith.miranda@bmv3.demo.local",
        "father_first_name": "Emilio", "father_last_name": "Miranda", "father_phone": "0918-555-0147",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.0, "height": 96.9,
    },
    {
        "account_num": 48, "username": "parent048", "first_name": "Ashley Kate", "middle_initial": "S", "last_name": "Salazar",
        "age": 3, "dob": "2023-03-04", "gender": "Female", "shift": "Afternoon",
        "street": "11 Ditas St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Katherine", "mother_last_name": "Salazar", "mother_phone": "0917-555-0148", "mother_email": "katherine.salazar@bmv3.demo.local",
        "father_first_name": "Severino", "father_last_name": "Salazar", "father_phone": "0918-555-0148",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.5, "height": 92.6,
    },
    {
        "account_num": 49, "username": "parent049", "first_name": "Adrian Gabriel", "middle_initial": "D", "last_name": "Dizon",
        "age": 4, "dob": "2022-07-30", "gender": "Male", "shift": "Afternoon",
        "street": "36 Waling-Waling St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Dolores", "mother_last_name": "Dizon", "mother_phone": "0917-555-0149", "mother_email": "dolores.dizon@bmv3.demo.local",
        "father_first_name": "Arthur", "father_last_name": "Dizon", "father_phone": "0918-555-0149",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.9, "height": 96.7,
    },
    {
        "account_num": 50, "username": "parent050", "first_name": "Kimberly Joy", "middle_initial": "F", "last_name": "Fabian",
        "age": 4, "dob": "2022-10-15", "gender": "Female", "shift": "Afternoon",
        "street": "19 Everlasting St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Flordeliza", "mother_last_name": "Fabian", "mother_phone": "0917-555-0150", "mother_email": "flordeliza.fabian@bmv3.demo.local",
        "father_first_name": "Felipe", "father_last_name": "Fabian", "father_phone": "0918-555-0150",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.2, "height": 95.3,
    },
    {
        "account_num": 51, "username": "parent051", "first_name": "Francis Leo", "middle_initial": "M", "last_name": "Mallari",
        "age": 4, "dob": "2022-02-09", "gender": "Male", "shift": "Afternoon",
        "street": "6 Jasmin St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Lucia", "mother_last_name": "Mallari", "mother_phone": "0917-555-0151", "mother_email": "lucia.mallari@bmv3.demo.local",
        "father_first_name": "Leandro", "father_last_name": "Mallari", "father_phone": "0918-555-0151",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.6, "height": 98.1,
    },
    {
        "account_num": 52, "username": "parent052", "first_name": "Hailey Mae", "middle_initial": "G", "last_name": "Galang",
        "age": 4, "dob": "2022-06-21", "gender": "Female", "shift": "Afternoon",
        "street": "15 Bougainvillea St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Gina", "mother_last_name": "Galang", "mother_phone": "0917-555-0152", "mother_email": "gina.galang@bmv3.demo.local",
        "father_first_name": "Gilberto", "father_last_name": "Galang", "father_phone": "0918-555-0152",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.1, "height": 95.0,
    },
    {
        "account_num": 53, "username": "parent053", "first_name": "Vincent Paul", "middle_initial": "S", "last_name": "Samson",
        "age": 4, "dob": "2022-11-12", "gender": "Male", "shift": "Afternoon",
        "street": "28 Daisy St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Silvia", "mother_last_name": "Samson", "mother_phone": "0917-555-0153", "mother_email": "silvia.samson@bmv3.demo.local",
        "father_first_name": "Vicente", "father_last_name": "Samson", "father_phone": "0918-555-0153",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.7, "height": 96.2,
    },
    {
        "account_num": 54, "username": "parent054", "first_name": "Kyra Jade", "middle_initial": "T", "last_name": "Tungol",
        "age": 3, "dob": "2023-04-01", "gender": "Female", "shift": "Afternoon",
        "street": "7 Lotus St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Teresita", "mother_last_name": "Tungol", "mother_phone": "0917-555-0154", "mother_email": "teresita.tungol@bmv3.demo.local",
        "father_first_name": "Teodoro", "father_last_name": "Tungol", "father_phone": "0918-555-0154",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.4, "height": 92.3,
    },
    {
        "account_num": 55, "username": "parent055", "first_name": "Justine Carl", "middle_initial": "D", "last_name": "Dionisio",
        "age": 4, "dob": "2022-01-18", "gender": "Male", "shift": "Afternoon",
        "street": "13 Gardenia St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Daisy", "mother_last_name": "Dionisio", "mother_phone": "0917-555-0155", "mother_email": "daisy.dionisio@bmv3.demo.local",
        "father_first_name": "Danilo", "father_last_name": "Dionisio", "father_phone": "0918-555-0155",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.7, "height": 98.4,
    },
    {
        "account_num": 56, "username": "parent056", "first_name": "Raine Monique", "middle_initial": "C", "last_name": "Cayabyab",
        "age": 4, "dob": "2022-08-27", "gender": "Female", "shift": "Afternoon",
        "street": "32 Zinnia St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Clarita", "mother_last_name": "Cayabyab", "mother_phone": "0917-555-0156", "mother_email": "clarita.cayabyab@bmv3.demo.local",
        "father_first_name": "Crisanto", "father_last_name": "Cayabyab", "father_phone": "0918-555-0156",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.3, "height": 95.5,
    },
    {
        "account_num": 57, "username": "parent057", "first_name": "Kenneth Troy", "middle_initial": "M", "last_name": "Macaraeg",
        "age": 4, "dob": "2022-04-14", "gender": "Male", "shift": "Afternoon",
        "street": "20 Marigold St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Maybelline", "mother_last_name": "Macaraeg", "mother_phone": "0917-555-0157", "mother_email": "maybelline.macaraeg@bmv3.demo.local",
        "father_first_name": "Manuel", "father_last_name": "Macaraeg", "father_phone": "0918-555-0157",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.1, "height": 97.0,
    },
    {
        "account_num": 58, "username": "parent058", "first_name": "Lyra Gwyneth", "middle_initial": "A", "last_name": "Angeles",
        "age": 4, "dob": "2022-09-02", "gender": "Female", "shift": "Afternoon",
        "street": "16 Magnolia St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Annaliza", "mother_last_name": "Angeles", "mother_phone": "0917-555-0158", "mother_email": "annaliza.angeles@bmv3.demo.local",
        "father_first_name": "Armando", "father_last_name": "Angeles", "father_phone": "0918-555-0158",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.9, "height": 94.6,
    },
    {
        "account_num": 59, "username": "parent059", "first_name": "Aaron Miguel", "middle_initial": "S", "last_name": "Sison",
        "age": 4, "dob": "2022-05-27", "gender": "Male", "shift": "Afternoon",
        "street": "9 Azucena St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Sandra", "mother_last_name": "Sison", "mother_phone": "0917-555-0159", "mother_email": "sandra.sison@bmv3.demo.local",
        "father_first_name": "Simplicio", "father_last_name": "Sison", "father_phone": "0918-555-0159",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.8, "height": 96.4,
    },
    {
        "account_num": 60, "username": "parent060", "first_name": "Danica Rose", "middle_initial": "L", "last_name": "Laxamana",
        "age": 4, "dob": "2022-07-12", "gender": "Female", "shift": "Afternoon",
        "street": "23 Begonia St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Leticia", "mother_last_name": "Laxamana", "mother_phone": "0917-555-0160", "mother_email": "leticia.laxamana@bmv3.demo.local",
        "father_first_name": "Leocadio", "father_last_name": "Laxamana", "father_phone": "0918-555-0160",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.4, "height": 95.8,
    },
    {
        "account_num": 61, "username": "parent061", "first_name": "Liam Nathan", "middle_initial": "V", "last_name": "Bernardo",
        "age": 4, "dob": "2022-09-12", "gender": "Male", "shift": "Afternoon",
        "street": "14 Rosal St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Grace", "mother_last_name": "Bernardo", "mother_phone": "0917-555-0161", "mother_email": "grace.bernardo@bmv3.demo.local",
        "father_first_name": "Mark", "father_last_name": "Bernardo", "father_phone": "0918-555-0161",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.0, "height": 96.8,
    },
    {
        "account_num": 62, "username": "parent062", "first_name": "Sophia Gabrielle", "middle_initial": "D", "last_name": "Atienza",
        "age": 4, "dob": "2022-11-05", "gender": "Female", "shift": "Afternoon",
        "street": "28 Sampaguita St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Teresa", "mother_last_name": "Atienza", "mother_phone": "0917-555-0162", "mother_email": "teresa.atienza@bmv3.demo.local",
        "father_first_name": "Jeffrey", "father_last_name": "Atienza", "father_phone": "0918-555-0162",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.9, "height": 94.7,
    },
    {
        "account_num": 63, "username": "parent063", "first_name": "Enzo Rafael", "middle_initial": "C", "last_name": "De Castro",
        "age": 4, "dob": "2022-04-18", "gender": "Male", "shift": "Afternoon",
        "street": "5 Ditas St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Clarissa", "mother_last_name": "De Castro", "mother_phone": "0917-555-0163", "mother_email": "clarissa.decastro@bmv3.demo.local",
        "father_first_name": "Ronald", "father_last_name": "De Castro", "father_phone": "0918-555-0163",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.3, "height": 97.4,
    },
    {
        "account_num": 64, "username": "parent064", "first_name": "Brianna Nicole", "middle_initial": "I", "last_name": "Ilagan",
        "age": 3, "dob": "2023-03-24", "gender": "Female", "shift": "Afternoon",
        "street": "42 Ilang-Ilang St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Melissa", "mother_last_name": "Ilagan", "mother_phone": "0917-555-0164", "mother_email": "melissa.ilagan@bmv3.demo.local",
        "father_first_name": "Paulo", "father_last_name": "Ilagan", "father_phone": "0918-555-0164",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.6, "height": 92.8,
    },
    {
        "account_num": 65, "username": "parent065", "first_name": "Kenji Matthew", "middle_initial": "M", "last_name": "Macatangay",
        "age": 4, "dob": "2022-08-30", "gender": "Male", "shift": "Afternoon",
        "street": "19 Gumamela St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Michelle", "mother_last_name": "Macatangay", "mother_phone": "0917-555-0165", "mother_email": "michelle.macatangay@bmv3.demo.local",
        "father_first_name": "Dennis", "father_last_name": "Macatangay", "father_phone": "0918-555-0165",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.8, "height": 96.3,
    },
    {
        "account_num": 66, "username": "parent066", "first_name": "Juliana Faye", "middle_initial": "D", "last_name": "Dimaculangan",
        "age": 4, "dob": "2022-06-15", "gender": "Female", "shift": "Afternoon",
        "street": "8 Cattleya St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Bernadette", "mother_last_name": "Dimaculangan", "mother_phone": "0917-555-0166", "mother_email": "bernadette.dimaculangan@bmv3.demo.local",
        "father_first_name": "Allan", "father_last_name": "Dimaculangan", "father_phone": "0918-555-0166",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.2, "height": 95.1,
    },
    {
        "account_num": 67, "username": "parent067", "first_name": "Cedric James", "middle_initial": "H", "last_name": "Hernandez",
        "age": 4, "dob": "2021-12-08", "gender": "Male", "shift": "Afternoon",
        "street": "33 Dahlia St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Christine", "mother_last_name": "Hernandez", "mother_phone": "0917-555-0167", "mother_email": "christine.hernandez@bmv3.demo.local",
        "father_first_name": "Joel", "father_last_name": "Hernandez", "father_phone": "0918-555-0167",
        "allergies": "None reported", "health_conditions": "None", "weight": 16.0, "height": 99.0,
    },
    {
        "account_num": 68, "username": "parent068", "first_name": "Patricia Mae", "middle_initial": "M", "last_name": "Malabanan",
        "age": 4, "dob": "2022-07-19", "gender": "Female", "shift": "Afternoon",
        "street": "12 Waling-Waling St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Jocelyn", "mother_last_name": "Malabanan", "mother_phone": "0917-555-0168", "mother_email": "jocelyn.malabanan@bmv3.demo.local",
        "father_first_name": "Richard", "father_last_name": "Malabanan", "father_phone": "0918-555-0168",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.1, "height": 95.3,
    },
    {
        "account_num": 69, "username": "parent069", "first_name": "Sean Patrick", "middle_initial": "L", "last_name": "Laurel",
        "age": 3, "dob": "2023-01-28", "gender": "Male", "shift": "Afternoon",
        "street": "21 Jasmin St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Angela", "mother_last_name": "Laurel", "mother_phone": "0917-555-0169", "mother_email": "angela.laurel@bmv3.demo.local",
        "father_first_name": "Christian", "father_last_name": "Laurel", "father_phone": "0918-555-0169",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.7, "height": 93.3,
    },
    {
        "account_num": 70, "username": "parent070", "first_name": "Samantha Jane", "middle_initial": "R", "last_name": "Recto",
        "age": 4, "dob": "2022-10-14", "gender": "Female", "shift": "Afternoon",
        "street": "16 Lotus St.", "purok": "Purok 5", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Vivian", "mother_last_name": "Recto", "mother_phone": "0917-555-0170", "mother_email": "vivian.recto@bmv3.demo.local",
        "father_first_name": "Eduardo", "father_last_name": "Recto", "father_phone": "0918-555-0170",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.3, "height": 95.7,
    },
    {
        "account_num": 71, "username": "parent071", "first_name": "Miguel Antonio", "middle_initial": "M", "last_name": "Marasigan",
        "age": 4, "dob": "2022-05-22", "gender": "Male", "shift": "Afternoon",
        "street": "9 Camia St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Katrina", "mother_last_name": "Marasigan", "mother_phone": "0917-555-0171", "mother_email": "katrina.marasigan@bmv3.demo.local",
        "father_first_name": "Patrick", "father_last_name": "Marasigan", "father_phone": "0918-555-0171",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.2, "height": 97.5,
    },
    {
        "account_num": 72, "username": "parent072", "first_name": "Kimberly Denise", "middle_initial": "A", "last_name": "Arriola",
        "age": 4, "dob": "2022-09-03", "gender": "Female", "shift": "Afternoon",
        "street": "30 Gardenia St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Cynthia", "mother_last_name": "Arriola", "mother_phone": "0917-555-0172", "mother_email": "cynthia.arriola@bmv3.demo.local",
        "father_first_name": "Gary", "father_last_name": "Arriola", "father_phone": "0918-555-0172",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.0, "height": 95.0,
    },
    {
        "account_num": 73, "username": "parent073", "first_name": "Andrei Louise", "middle_initial": "K", "last_name": "Katigbak",
        "age": 3, "dob": "2023-02-17", "gender": "Male", "shift": "Afternoon",
        "street": "7 Everlasting St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Rochelle", "mother_last_name": "Katigbak", "mother_phone": "0917-555-0173", "mother_email": "rochelle.katigbak@bmv3.demo.local",
        "father_first_name": "Vincent", "father_last_name": "Katigbak", "father_phone": "0918-555-0173",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.8, "height": 93.4,
    },
    {
        "account_num": 74, "username": "parent074", "first_name": "Janella Marie", "middle_initial": "O", "last_name": "Ona",
        "age": 4, "dob": "2022-08-11", "gender": "Female", "shift": "Afternoon",
        "street": "24 Bougainvillea St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Marita", "mother_last_name": "Ona", "mother_phone": "0917-555-0174", "mother_email": "marita.ona@bmv3.demo.local",
        "father_first_name": "Gerald", "father_last_name": "Ona", "father_phone": "0918-555-0174",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.4, "height": 95.9,
    },
    {
        "account_num": 75, "username": "parent075", "first_name": "Kyle Brandon", "middle_initial": "C", "last_name": "Cueto",
        "age": 4, "dob": "2021-11-29", "gender": "Male", "shift": "Afternoon",
        "street": "18 Daisy St.", "purok": "Purok 5", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Evelyn", "mother_last_name": "Cueto", "mother_phone": "0917-555-0175", "mother_email": "evelyn.cueto@bmv3.demo.local",
        "father_first_name": "Anthony", "father_last_name": "Cueto", "father_phone": "0918-555-0175",
        "allergies": "None reported", "health_conditions": "None", "weight": 16.1, "height": 99.2,
    },
    {
        "account_num": 76, "username": "parent076", "first_name": "Princess Diana", "middle_initial": "M", "last_name": "Montalbo",
        "age": 4, "dob": "2022-04-07", "gender": "Female", "shift": "Afternoon",
        "street": "11 Zinnia St.", "purok": "Purok 2", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Sheryl", "mother_last_name": "Montalbo", "mother_phone": "0917-555-0176", "mother_email": "sheryl.montalbo@bmv3.demo.local",
        "father_first_name": "Raymund", "father_last_name": "Montalbo", "father_phone": "0918-555-0176",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.1, "height": 95.1,
    },
    {
        "account_num": 77, "username": "parent077", "first_name": "Rafael Lorenzo", "middle_initial": "C", "last_name": "Caringal",
        "age": 4, "dob": "2022-12-16", "gender": "Male", "shift": "Afternoon",
        "street": "26 Marigold St.", "purok": "Purok 3", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Gina", "mother_last_name": "Caringal", "mother_phone": "0917-555-0177", "mother_email": "gina.caringal@bmv3.demo.local",
        "father_first_name": "Manuel", "father_last_name": "Caringal", "father_phone": "0918-555-0177",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.9, "height": 96.6,
    },
    {
        "account_num": 78, "username": "parent078", "first_name": "Jasmine Chloe", "middle_initial": "A", "last_name": "Agoncillo",
        "age": 3, "dob": "2023-05-04", "gender": "Female", "shift": "Afternoon",
        "street": "4 Magnolia St.", "purok": "Purok 4", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Lea", "mother_last_name": "Agoncillo", "mother_phone": "0917-555-0178", "mother_email": "lea.agoncillo@bmv3.demo.local",
        "father_first_name": "Ferdinand", "father_last_name": "Agoncillo", "father_phone": "0918-555-0178",
        "allergies": "None reported", "health_conditions": "None", "weight": 13.5, "height": 92.4,
    },
    {
        "account_num": 79, "username": "parent079", "first_name": "Paul Christian", "middle_initial": "B", "last_name": "Barte",
        "age": 4, "dob": "2022-07-26", "gender": "Male", "shift": "Afternoon",
        "street": "37 Azucena St.", "purok": "Purok 1", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Joanne", "mother_last_name": "Barte", "mother_phone": "0917-555-0179", "mother_email": "joanne.barte@bmv3.demo.local",
        "father_first_name": "Christopher", "father_last_name": "Barte", "father_phone": "0918-555-0179",
        "allergies": "None reported", "health_conditions": "None", "weight": 15.3, "height": 97.6,
    },
    {
        "account_num": 80, "username": "parent080", "first_name": "Christine Angela", "middle_initial": "P", "last_name": "Punzalan",
        "age": 4, "dob": "2022-10-09", "gender": "Female", "shift": "Afternoon",
        "street": "15 Begonia St.", "purok": "Purok 5", "barangay": "Market View", "city_municipality": "Lucena City",
        "mother_first_name": "Maribel", "mother_last_name": "Punzalan", "mother_phone": "0917-555-0180", "mother_email": "maribel.punzalan@bmv3.demo.local",
        "father_first_name": "Arthur", "father_last_name": "Punzalan", "father_phone": "0918-555-0180",
        "allergies": "None reported", "health_conditions": "None", "weight": 14.1, "height": 95.3,
    },
]


class Command(BaseCommand):
    help = "Seed School Year 2026-2027 (starts 1st week of July 2026, ends last week of April 2027) with 80 pupils attached to 80 parent accounts, rich attendance up to Nov 3, nutrition, milestones, announcements, and highlights."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=" * 80))
        self.stdout.write(self.style.NOTICE("  BMV3 CHILD DEVELOPMENT CENTER - ACTIVE SCHOOL YEAR SEEDING"))
        self.stdout.write(self.style.NOTICE("  School Year: 2026-2027 (July 6, 2026 to April 30, 2027)"))
        self.stdout.write(self.style.NOTICE("  Current Date Snapshot: November 3, 2026 (Tuesday)"))
        self.stdout.write(self.style.NOTICE("=" * 80))

        today = datetime.date(2026, 11, 3)
        sy_start = datetime.date(2026, 7, 6)   # First Monday of July 2026
        sy_end = datetime.date(2027, 4, 30)    # Last Friday of April 2027

        with transaction.atomic():
            # 1. School Year 2025-2026 (Archive)
            hist_sy, _ = SchoolYear.objects.get_or_create(
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
            hist_sy.save()

            # 2. School Year 2026-2027 (Current Active Year)
            active_sy, _ = SchoolYear.objects.get_or_create(
                name="2026-2027",
                defaults={
                    "is_active": True,
                    "start_date": sy_start,
                    "end_date": sy_end,
                    "eccd_1st_start": sy_start,
                    "eccd_1st_end": datetime.date(2026, 8, 7),
                    "eccd_2nd_start": today,
                    "eccd_2nd_end": datetime.date(2026, 12, 4),
                    "eccd_3rd_start": datetime.date(2027, 4, 5),
                    "eccd_3rd_end": sy_end,
                    "is_deleted": False,
                }
            )
            active_sy.start_date = sy_start
            active_sy.end_date = sy_end
            active_sy.eccd_1st_start = sy_start
            active_sy.eccd_1st_end = datetime.date(2026, 8, 7)
            active_sy.eccd_2nd_start = today
            active_sy.eccd_2nd_end = datetime.date(2026, 12, 4)
            active_sy.eccd_3rd_start = datetime.date(2027, 4, 5)
            active_sy.eccd_3rd_end = sy_end
            active_sy.is_active = True
            active_sy.is_deleted = False
            active_sy.save()

            # Ensure strictly only active_sy is active
            SchoolYear.objects.exclude(id=active_sy.id).update(is_active=False)
            self.stdout.write(self.style.SUCCESS(f"[1/8] School Year 2026-2027 configured ({sy_start} to {sy_end})."))

            # Update Enrollment Info
            ei = EnrollmentInfo.objects.first()
            if not ei:
                ei = EnrollmentInfo.objects.create(school_year=active_sy)
            ei.school_year = active_sy
            ei.program_name = "Child Development Program 2026–2027"
            ei.start_date = datetime.date(2026, 6, 1)
            ei.end_date = datetime.date(2026, 7, 3)
            ei.available_slots = 80
            ei.is_active = True
            ei.save()

            # Teacher profile for evaluations
            teacher_profile = UserProfile.objects.filter(is_teacher=True).first()
            if not teacher_profile:
                admin_u = User.objects.filter(is_superuser=True).first()
                if admin_u:
                    teacher_profile, _ = UserProfile.objects.get_or_create(user=admin_u, defaults={"is_teacher": True})

            # Clean previous 2026-2027 records to prevent duplicate piling
            Child.objects.filter(school_year=active_sy).delete()
            AttendanceRecord.objects.filter(school_year=active_sy).delete()
            NutritionRecord.objects.filter(school_year=active_sy).delete()
            BMIRecord.objects.filter(school_year=active_sy).delete()
            ECCDAssessment.objects.filter(school_year=active_sy).delete()

            # 3. Provision 80 Parent Accounts & 80 Enrolled Children
            self.stdout.write(self.style.NOTICE("[2/8] Creating 80 Pupil Records & Linking to 80 Parent Accounts..."))
            enrolled_children = []
            csv_rows = []

            for p in ACTIVE_CHILDREN_PROFILES:
                i = p["account_num"]
                acc_num = f"{i:03d}"
                username = f"parent{acc_num}"
                temp_password = f"Bmv3!Parent{acc_num}#"
                email = p["mother_email"]
                guardian_full_name = f"{p['mother_first_name']} {p['mother_last_name']}"

                # Ensure parent User exists
                user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": email,
                        "first_name": p["mother_first_name"],
                        "last_name": p["mother_last_name"],
                    }
                )
                user.set_password(temp_password)
                user.email = email
                user.first_name = p["mother_first_name"]
                user.last_name = p["mother_last_name"]
                user.is_active = True
                user.save()

                # UserProfile with home coordinates jittered across Lucena City Market View
                base_lat = Decimal("13.9380")
                base_lng = Decimal("121.6146")
                jitter_lat = Decimal(str(round(((i * 7) % 31 - 15) * 0.00045, 6)))
                jitter_lng = Decimal(str(round(((i * 13) % 29 - 14) * 0.00055, 6)))

                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "is_teacher": False,
                        "first_login": False,
                        "home_latitude": base_lat + jitter_lat,
                        "home_longitude": base_lng + jitter_lng,
                        "home_address_text": f"{p['street']}, {p['purok']}, Barangay Market View, Lucena City",
                    }
                )
                profile.is_teacher = False
                profile.first_login = False
                profile.home_latitude = base_lat + jitter_lat
                profile.home_longitude = base_lng + jitter_lng
                profile.home_address_text = f"{p['street']}, {p['purok']}, Barangay Market View, Lucena City"
                profile.save()

                # Create Child record in active school year
                dob_d = datetime.datetime.strptime(p["dob"], "%Y-%m-%d").date()
                child = Child.objects.create(
                    first_name=p["first_name"],
                    middle_initial=p["middle_initial"],
                    last_name=p["last_name"],
                    age=p["age"],
                    dob=dob_d,
                    doe=sy_start,
                    gender=p["gender"],
                    shift=p["shift"],
                    school_year=active_sy,
                    enrollment_status="Enrolled",
                    attendance_status="Present",
                    allergies=p["allergies"],
                    health_conditions=p["health_conditions"],
                    weight=p["weight"],
                    height=p["height"],
                    street=p["street"],
                    purok=p["purok"],
                    barangay=p["barangay"],
                    city_municipality=p["city_municipality"],
                    mother_first_name=p["mother_first_name"],
                    mother_last_name=p["mother_last_name"],
                    mother_phone=p["mother_phone"],
                    mother_email=p["mother_email"],
                    mother_address=f"{p['street']}, {p['purok']}, {p['barangay']}, {p['city_municipality']}",
                    father_first_name=p["father_first_name"],
                    father_last_name=p["father_last_name"],
                    father_phone=p["father_phone"],
                    phone=p["mother_phone"],
                    email=p["mother_email"],
                )

                # Link Child directly to parent's UserProfile
                child.parents.add(profile)
                enrolled_children.append(child)

                csv_rows.append({
                    "Account": i,
                    "Username": username,
                    "Temporary Password": temp_password,
                    "Parent / Guardian Name": guardian_full_name,
                    "Assigned Pupil": f"{child.first_name} {child.last_name}",
                    "Shift": child.shift,
                    "First Login Password Change": "Active This School Year",
                })

            # Also ensure Sky Dylan Villanueva (linked to jeremy_960) is present
            sky_child = Child.objects.create(
                first_name="Sky Dylan",
                middle_initial="T",
                last_name="Villanueva",
                age=3,
                dob=datetime.date(2023, 3, 15),
                doe=sy_start,
                gender="Male",
                shift="Morning",
                school_year=active_sy,
                enrollment_status="Enrolled",
                attendance_status="Present",
                allergies="Dairy / Milk",
                health_conditions="",
                weight=14.5,
                height=95.0,
                street="Purok Central",
                purok="Purok Central",
                barangay="Mayao Parada",
                city_municipality="Lucena City",
                father_first_name="Jeremy",
                father_middle_initial="T",
                father_last_name="Villanueva",
                father_phone="09053997797",
                father_email="jeremy_960@bmv3.local",
            )
            jeremy_user = User.objects.filter(username="jeremy_960").first()
            if jeremy_user and hasattr(jeremy_user, "userprofile"):
                sky_child.parents.add(jeremy_user.userprofile)
            enrolled_children.append(sky_child)

            self.stdout.write(self.style.SUCCESS(f"  [OK] Enrolled {len(enrolled_children)} total pupils in SY 2026-2027 (41 Morning, 40 Afternoon)."))

            # 4. Export CSVs with credentials
            root_dir = Path(settings.BASE_DIR).parent
            csv_paths = [
                root_dir / "bmv3_80_demo_parent_credentials.csv",
                Path(settings.BASE_DIR) / "bmv3_80_demo_parent_credentials.csv",
            ]
            for cp in csv_paths:
                try:
                    with open(cp, mode="w", newline="", encoding="utf-8") as f:
                        fieldnames = ["Account", "Username", "Temporary Password", "Parent / Guardian Name", "Assigned Pupil", "Shift", "First Login Password Change"]
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(csv_rows)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Could not write CSV {cp}: {e}"))

            # 5. Seed Attendance Records (July 6, 2026 to November 3, 2026)
            self.stdout.write(self.style.NOTICE("[3/8] Generating Daily Attendance & Dropoff/Pickup Data (July 6 to Nov 3)..."))
            holidays = {
                datetime.date(2026, 8, 21): "Ninoy Aquino Day",
                datetime.date(2026, 8, 31): "National Heroes Day",
                datetime.date(2026, 11, 2): "All Souls Day",
            }
            # Record NoClassDays
            for h_date, h_reason in holidays.items():
                NoClassDay.objects.get_or_create(date=h_date, defaults={"reason": h_reason, "school_year": active_sy})

            school_days = []
            cur_d = sy_start
            while cur_d <= today:
                # Regular daycare schedule is Monday to Thursday (0, 1, 2, 3). Fridays are available for special events.
                if cur_d.weekday() < 4 and cur_d not in holidays:
                    school_days.append(cur_d)
                cur_d += datetime.timedelta(days=1)

            absence_reasons = [
                "Common cold and fever",
                "Severe cough and throat congestion",
                "Inclement monsoon weather / heavy localized rain",
                "Family out of town",
                "Mild tummy ache",
                "Scheduled pediatric wellness visit",
            ]

            morning_times = ["07:40 AM", "07:44 AM", "07:48 AM", "07:52 AM", "07:55 AM"]
            afternoon_times = ["12:44 PM", "12:48 PM", "12:51 PM", "12:55 PM"]

            attendance_batch = []
            for d in school_days:
                is_today = (d == today)
                for ch in enrolled_children:
                    g_name = f"{ch.mother_first_name} {ch.mother_last_name}".strip() if ch.mother_first_name else f"{ch.father_first_name} {ch.father_last_name}".strip()
                    g_label = f"{g_name} ({'Mother' if ch.mother_first_name else 'Father'})"
                    sess = ch.shift

                    if not is_today:
                        # Historical date
                        r_val = (ch.id * 37 + d.toordinal() * 19) % 100
                        if r_val < 92:  # 92% Present
                            status = "Present"
                            drop_time = morning_times[(ch.id + d.day) % len(morning_times)] if sess == "Morning" else afternoon_times[(ch.id + d.day) % len(afternoon_times)]
                            pick_status = "Picked up on time"
                            reason = None
                        elif r_val < 97:  # 5% Late
                            status = "Late"
                            drop_time = "08:18 AM" if sess == "Morning" else "01:20 PM"
                            pick_status = "Picked up on time"
                            reason = None
                        else:  # 3% Absent
                            status = "Absent"
                            drop_time = None
                            pick_status = None
                            reason = absence_reasons[(ch.id + d.day) % len(absence_reasons)]

                        attendance_batch.append(
                            AttendanceRecord(
                                child=ch,
                                school_year=active_sy,
                                date=d,
                                status=status,
                                session=sess,
                                dropoff_time=drop_time,
                                pickup_status=pick_status,
                                authorized_guardian=g_label,
                                absence_reason=reason,
                            )
                        )
                    else:
                        # TODAY (Nov 3, 2026 - current date snapshot)
                        if sess == "Morning":
                            # 38 present, 2 late, 1 absent
                            mod = ch.id % 41
                            if mod == 0:
                                status = "Absent"
                                drop_time = None
                                pick_status = None
                                reason = "Mild pediatric asthma cough and congestion"
                            elif mod in (5, 23):
                                status = "Late"
                                drop_time = "08:15 AM"
                                pick_status = "Checked In"
                                reason = None
                            else:
                                status = "Present"
                                drop_time = morning_times[ch.id % len(morning_times)]
                                pick_status = "Checked In"
                                reason = None
                        else:
                            # Afternoon shift has NOT started yet today (Nov 3 morning).
                            # Leave unrecorded so teachers can take attendance using the [Present] [Absent] [Late] buttons.
                            continue

                        attendance_batch.append(
                            AttendanceRecord(
                                child=ch,
                                school_year=active_sy,
                                date=d,
                                status=status,
                                session=sess,
                                dropoff_time=drop_time,
                                pickup_status=pick_status,
                                authorized_guardian=g_label,
                                absence_reason=reason,
                            )
                        )

            AttendanceRecord.objects.bulk_create(attendance_batch, batch_size=1000)
            self.stdout.write(self.style.SUCCESS(f"  [OK] Created {len(attendance_batch)} attendance logs ({len(school_days)} school days)."))

            # 6. Seed Supplementary Nutrition Records (Mon & Wed from July 6 to Nov 3)
            self.stdout.write(self.style.NOTICE("[4/8] Generating Nutrition & Feeding Records (July 6 to Nov 3)..."))
            nutrition_days = [d for d in school_days if d.weekday() in (0, 2) or d == today]
            snack_templates = [
                ("Finished", "Ate entire portion of warm chicken arroz caldo with egg and drank milk."),
                ("Finished", "Finished bowl of champorado with evaporated milk with great appetite."),
                ("Finished", "Ate whole boiled saba banana and finished clean water bottle."),
                ("Finished", "Ate entire pandesal with scrambled egg and shared happily with classmates."),
                ("Finished", "Finished delicious macaroni sopas with shredded chicken and carrots."),
                ("Finished", "Finished fresh sliced ripe papaya and sweet potato (kamote)."),
                ("Some Left", "Ate half portion of lugaw with malunggay; drank entire glass of water."),
                ("Some Left", "Ate some biscuits and fruits; left small portion of porridge."),
                ("Not Eaten", "Did not feel like eating snack today due to mild teething discomfort."),
            ]

            nutrition_batch = []
            for d in nutrition_days:
                is_today = (d == today)
                for ch in enrolled_children:
                    if is_today:
                        status = "Finished"
                        notes = "Ate warm chicken arroz caldo with hard-boiled egg and fresh malunggay leaves."
                    else:
                        pick_idx = (ch.id * 31 + d.day * 17) % len(snack_templates)
                        status, notes = snack_templates[pick_idx]

                    nutrition_batch.append(
                        NutritionRecord(
                            child=ch,
                            school_year=active_sy,
                            date=d,
                            snack_status=status,
                            teacher_notes=notes,
                        )
                    )

            NutritionRecord.objects.bulk_create(nutrition_batch, batch_size=1000)
            self.stdout.write(self.style.SUCCESS(f"  [OK] Created {len(nutrition_batch)} nutrition records across {len(nutrition_days)} feeding days."))

            # 7. Seed Monthly BMI Records (July to October - End of Month)
            self.stdout.write(self.style.NOTICE("[5/8] Generating Monthly BMI Records (July to October - End of Month)..."))
            bmi_batch = []
            bmi_months = [
                ("Jul", datetime.date(2026, 7, 31), -0.6, -1.8),
                ("Aug", datetime.date(2026, 8, 31), -0.4, -1.2),
                ("Sep", datetime.date(2026, 9, 30), -0.2, -0.6),
                ("Oct", datetime.date(2026, 10, 31), 0.0, 0.0),
            ]

            for ch in enrolled_children:
                final_w = ch.weight or 14.5
                final_h = ch.height or 97.0

                for m_code, m_date, w_offset, h_offset in bmi_months:
                    m_weight = round(final_w + w_offset, 1)
                    m_height = round(final_h + h_offset, 1)

                    bmi_batch.append(
                        BMIRecord(
                            child=ch,
                            school_year=active_sy,
                            quarter=m_code,
                            weight=m_weight,
                            height=m_height,
                            measurement_date=m_date,
                            status="Finalized"
                        )
                    )

                # Ensure child's current weight and height reflect latest October measurement
                Child.objects.filter(pk=ch.pk).update(weight=final_w, height=final_h)

            BMIRecord.objects.bulk_create(bmi_batch, batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"  [OK] Created {len(bmi_batch)} Monthly BMI health measurements (July, August, September, October)."))

            # 8. Seed ECCD Milestone Assessments (1st Period Finalized, 2nd Period Today)
            self.stdout.write(self.style.NOTICE("[6/8] Generating ECCD Developmental Milestone Evaluations..."))
            milestones = list(ECCDMilestone.objects.all().order_by('domain__order', 'order_number'))
            assessments_to_score = []

            for idx, ch in enumerate(enrolled_children, 1):
                # 1st Period Evaluation (Baseline - July 27, 2026)
                a1 = ECCDAssessment.objects.create(
                    child=ch,
                    school_year=active_sy,
                    teacher=teacher_profile,
                    assessment_period="1st",
                    assessment_date=datetime.date(2026, 7, 27),
                    status="Finalized",
                    remarks="Baseline assessment completed at start of SY 2026–2027. Demonstrates good center routine adaptation.",
                    strengths="Active participation in group songs, polite greetings, friendly socialization.",
                    concerns="Developing fine-motor dexterity with crayons and safety scissors.",
                    follow_up_action="Continue daily manipulation of playdough and threading large beads."
                )
                assessments_to_score.append((a1, "1st", idx))

                # 2nd Period Evaluation (Mid-Year - November 3, 2026)
                a2 = ECCDAssessment.objects.create(
                    child=ch,
                    school_year=active_sy,
                    teacher=teacher_profile,
                    assessment_period="2nd",
                    assessment_date=today,
                    status="Draft",
                    remarks="Mid-year assessment in progress as of November 3, 2026. Significant growth in self-help and language skills.",
                    strengths="Independent handwashing, speaks in clear complete sentences, counts 1 to 10 reliably.",
                    concerns="Needs gentle reminders to sustain focus during sedentary listening tasks.",
                    follow_up_action="Integrate physical movement breaks between structured activities."
                )
                assessments_to_score.append((a2, "2nd", idx))

                # Simple MilestoneRecord
                MilestoneRecord.objects.update_or_create(
                    child=ch,
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

                # ECCDBookletRecord
                ECCDBookletRecord.objects.update_or_create(
                    child=ch,
                    defaults={
                        "sociodemographic": {
                            "child_name": f"{ch.first_name} {ch.middle_initial or ''} {ch.last_name}".strip(),
                            "sex": ch.gender,
                            "dob": str(ch.dob),
                            "address": f"{ch.street}, {ch.purok}, {ch.barangay}, {ch.city_municipality}",
                            "mother_name": f"{ch.mother_first_name} {ch.mother_last_name}",
                            "father_name": f"{ch.father_first_name} {ch.father_last_name}",
                            "emergency_contact": ch.phone,
                        },
                        "health_record": {
                            "immunizations": "Complete (BCG, DPT, Polio, Measles)",
                            "hearing": "Normal",
                            "vision": "Normal",
                            "allergies": ch.allergies or "None",
                        },
                        "examiner_notes": {
                            "1st_period": "Baseline evaluation completed successfully.",
                            "2nd_period": "Mid-year checkup currently underway as of Nov 3.",
                        }
                    }
                )

            # Generate Scores for all milestones
            scores_batch = []
            for assess, period, ch_idx in assessments_to_score:
                for m in milestones:
                    m_hash = (ch_idx * 31 + m.id * 17) % 100
                    if period == "1st":
                        score = 2 if m_hash < 35 else (1 if m_hash < 88 else 0)
                    else:  # 2nd period: noticeable advancement
                        score = 2 if m_hash < 75 else (1 if m_hash < 96 else 0)

                    scores_batch.append(
                        ECCDMilestoneScore(
                            assessment=assess,
                            milestone=m,
                            teacher_score=score,
                            parent_score=score,
                            teacher_observation=f"Demonstrated appropriately during {period} assessment."
                        )
                    )

            ECCDMilestoneScore.objects.bulk_create(scores_batch, batch_size=2000)
            self.stdout.write(self.style.SUCCESS(f"  [OK] Generated {len(assessments_to_score)} ECCD Assessments and {len(scores_batch)} milestone scores."))

            # 9. Seed Activities and Student Completions for 2026-2027
            self.stdout.write(self.style.NOTICE("[7/8] Seeding Center Activities and Student Completions..."))
            activities_data = [
                ("Orientation & Welcome Circle", "Daycare opening orientation, classroom tour, and peer introduction games.", datetime.date(2026, 7, 10)),
                ("Nutrition Month Healthy Plate Making", "Paper plate art creating balanced Go, Grow, and Glow food models.", datetime.date(2026, 7, 24)),
                ("Buwan ng Wika Cultural Day", "Filipino cultural songs, traditional parlor games, and folk costume presentation.", datetime.date(2026, 8, 28)),
                ("Sensory Science & Nature Walk", "Hands-on leaf printing, tactile texture sorting, and garden exploration.", datetime.date(2026, 9, 22)),
                ("Global Handwashing & Oral Hygiene Workshop", "City Health team demonstration of proper 7-step handwashing and dental care.", datetime.date(2026, 10, 15)),
            ]
            completions_batch = []
            for act_name, act_desc, act_date in activities_data:
                act, _ = Activity.objects.get_or_create(
                    name=act_name,
                    school_year=active_sy,
                    defaults={"description": act_desc, "date": act_date}
                )
                for ch in enrolled_children:
                    completions_batch.append(
                        StudentActivityCompletion(
                            child=ch,
                            activity=act,
                            completed=True,
                            remarks="Actively engaged and successfully finished the learning activity."
                        )
                    )
            StudentActivityCompletion.objects.bulk_create(completions_batch, batch_size=1000)
            self.stdout.write(self.style.SUCCESS(f"  [OK] Created {len(activities_data)} activities with {len(completions_batch)} student completions."))

            # 10. Seed Announcements & Program Highlights
            self.stdout.write(self.style.NOTICE("[8/8] Seeding Realistic Center Announcements & Program Highlights..."))
            announcements_data = [
                {
                    "title": "Welcome to School Year 2026–2027!",
                    "category": "General",
                    "publish_date": datetime.date(2026, 7, 6),
                    "event_date": None,
                    "status": "Published",
                    "is_featured": True,
                    "is_important": False,
                    "description": "We warmly welcome all returning and new daycare pupils and families to Barangay Market View 3 Child Development Center for SY 2026–2027. Morning shift classes run 8:00 AM - 10:30 AM; afternoon shift classes run 1:00 PM - 3:30 PM.",
                },
                {
                    "title": "Nutrition Month 2026: 'Healthy Diet, Gawing Habit for Life'",
                    "category": "Events",
                    "publish_date": datetime.date(2026, 7, 14),
                    "event_date": datetime.date(2026, 7, 28),
                    "status": "Published",
                    "is_featured": False,
                    "is_important": False,
                    "description": "In celebration of National Nutrition Month, BMV3 CDC is holding weekly healthy snack demonstrations, fruit preparation activities, and nutrition lectures for parents throughout July.",
                },
                {
                    "title": "1st Assessment Period ECCD Developmental Evaluations",
                    "category": "Schedule",
                    "publish_date": datetime.date(2026, 7, 20),
                    "event_date": datetime.date(2026, 7, 27),
                    "status": "Published",
                    "is_featured": False,
                    "is_important": True,
                    "description": "ECCD checklist baseline evaluations for all morning and afternoon pupils will be administered from July 27 to August 7, 2026. Parents may review their child's baseline milestone summary on the portal.",
                },
                {
                    "title": "Buwan ng Wikang Pambansa Celebration & Cultural Presentations",
                    "category": "Activities",
                    "publish_date": datetime.date(2026, 8, 10),
                    "event_date": datetime.date(2026, 8, 28),
                    "status": "Published",
                    "is_featured": False,
                    "is_important": False,
                    "description": "Theme: 'Filipino: Wikang Mapagpalaya.' Pupils are encouraged to wear traditional Filipino costumes on Friday, August 28, 2026 for cultural songs, poetry, and native food sharing.",
                },
                {
                    "title": "Supplemental Feeding Program (SFP) Ongoing Implementation",
                    "category": "Health & Safety",
                    "publish_date": datetime.date(2026, 9, 14),
                    "event_date": None,
                    "status": "Published",
                    "is_featured": False,
                    "is_important": False,
                    "description": "The City Social Welfare & Development Office has provided fortified meal supplies for the center's 120-day Supplemental Feeding Program. Hot, nutritious snacks are served 3 times weekly.",
                },
                {
                    "title": "Global Handwashing Day & Oral Health Workshop",
                    "category": "Health & Safety",
                    "publish_date": datetime.date(2026, 10, 9),
                    "event_date": datetime.date(2026, 10, 15),
                    "status": "Published",
                    "is_featured": False,
                    "is_important": False,
                    "description": "The Lucena City Health team visited BMV3 to conduct interactive 7-step handwashing demonstrations and distribute complimentary dental hygiene kits to all enrolled daycare pupils.",
                },
                {
                    "title": "Commencement of 2nd Period ECCD Milestone Evaluations",
                    "category": "Important Notice",
                    "publish_date": datetime.date(2026, 11, 2),
                    "event_date": today,
                    "status": "Published",
                    "is_featured": True,
                    "is_important": True,
                    "description": "Mid-year developmental evaluations officially begin today, November 3, 2026. Teachers are assessing cognitive, language, motor, and self-help progress. Parent progress consultations will follow.",
                },
            ]

            for a_info in announcements_data:
                Announcement.objects.update_or_create(
                    title=a_info["title"],
                    defaults={
                        "category": a_info["category"],
                        "publish_date": a_info["publish_date"],
                        "event_date": a_info["event_date"],
                        "status": a_info["status"],
                        "is_featured": a_info["is_featured"],
                        "is_important": a_info["is_important"],
                        "description": a_info["description"],
                        "created_by": teacher_profile,
                    }
                )

            # Program Highlights
            highlights_data = [
                ("Opening Day of Classes - SY 2026–2027", "BMV3 Child Development Center kicked off the new school year welcoming 80 energetic pupils across the morning and afternoon cohorts with bright smiles and storytelling.", datetime.date(2026, 7, 6)),
                ("Culminating Nutrition Month Fruit Salad Fiesta", "Our little pupils wore colorful chef headbands, helped wash and mix nutritious seasonal fruit bowls, and learned the benefits of vitamins and minerals.", datetime.date(2026, 7, 31)),
                ("Buwan ng Wika: Sabayang Pag-awit at Katutubong Laro", "A vibrant celebration of Filipino heritage filled with traditional costumes, joyful Tagalog nursery rhymes, and classic games like piko and tumbang preso.", datetime.date(2026, 8, 28)),
                ("Interactive Sensory Discovery & Science Day", "Pupils explored kinetic sand, finger paints, water beads, and leaf sorting stations to build early cognitive curiosity, spatial sense, and tactile confidence.", datetime.date(2026, 9, 25)),
                ("Global Handwashing Day & Fluoride Dental Clinic", "In partnership with the Barangay Health Center, pupils mastered the 7 steps of proper handwashing with soap and clean water to keep germs away all year.", datetime.date(2026, 10, 15)),
            ]
            for h_title, h_desc, h_date in highlights_data:
                ProgramHighlight.objects.update_or_create(
                    title=h_title,
                    defaults={
                        "description": h_desc,
                        "date": h_date,
                    }
                )

        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write(self.style.SUCCESS("  SUCCESSFULLY SEEDED ACTIVE SCHOOL YEAR 2026-2027!"))
        self.stdout.write(self.style.SUCCESS(f"  Total Enrolled Pupils: {Child.objects.filter(school_year=active_sy).count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Total Attendance Logs: {AttendanceRecord.objects.filter(school_year=active_sy).count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Total Nutrition Records: {NutritionRecord.objects.filter(school_year=active_sy).count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Total BMI Records: {BMIRecord.objects.filter(school_year=active_sy).count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Total ECCD Assessments: {ECCDAssessment.objects.filter(school_year=active_sy).count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Total Announcements: {Announcement.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Total Program Highlights: {ProgramHighlight.objects.count()}"))
        self.stdout.write(self.style.SUCCESS("=" * 80))
