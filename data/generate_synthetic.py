import json
import random
import csv
from datetime import datetime, timedelta
import os

# Config
NUM_REQUESTS = 500
OUTPUT_FILE = "synthetic_requests.json"
DISTRICTS_FILE = "districts.csv"

# Time config
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=30)

def random_date():
    delta = END_DATE - START_DATE
    random_days = random.random() * delta.days
    return START_DATE + timedelta(days=random_days)

# District data
districts = []
if os.path.exists(DISTRICTS_FILE):
    with open(DISTRICTS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            districts.append(row)
else:
    print(f"Error: {DISTRICTS_FILE} not found. Ensure it is in the same directory.")
    exit(1)

# Map state to primary language
STATE_LANGUAGE_MAP = {
    "Uttar Pradesh": "Hindi",
    "Bihar": "Hindi",
    "Madhya Pradesh": "Hindi",
    "Rajasthan": "Hindi",
    "Haryana": "Hindi",
    "NCT of Delhi": "Hindi",
    "Tamil Nadu": "Tamil",
    "Telangana": "Telugu",
    "Andhra Pradesh": "Telugu",
    "Karnataka": "Kannada",
    "Maharashtra": "Marathi",
    "Gujarat": "Gujarati",
    "West Bengal": "Bengali",
    "Kerala": "Malayalam",
    "Odisha": "Odia",
    "Punjab": "Punjabi"
}

# Categories
CATEGORIES = ["ROADS", "WATER", "ELECTRICITY", "HEALTHCARE", "EDUCATION", "SANITATION", "DIGITAL"]

# Templates
TEMPLATES = {
    "Hindi": {
        "ROADS": [
            ("हमारे इलाके में सड़क बहुत खराब है, कई गड्ढे हैं।", "The road in our area is very bad, there are many potholes.", "NEGATIVE"),
            ("पिछले बारिश के बाद से मुख्य सड़क टूट गई है, कृपया मरम्मत करें।", "The main road is broken since the last rain, please repair it.", "NEGATIVE"),
            ("सड़क निर्माण का काम आधा अधूरा छोड़ दिया गया है।", "Road construction work has been left half incomplete.", "NEGATIVE")
        ],
        "WATER": [
            ("पिछले तीन दिनों से हमारे वार्ड में पानी नहीं आ रहा है।", "There has been no water supply in our ward for the last three days.", "NEGATIVE"),
            ("नल से बहुत गंदा पानी आ रहा है, पीने लायक नहीं है।", "Very dirty water is coming from the tap, it's not drinkable.", "NEGATIVE"),
            ("गर्मियों में पानी की बहुत किल्लत हो गई है, टैंकर भिजवाएं।", "There is a severe water shortage in summer, please send a tanker.", "NEGATIVE")
        ],
        "ELECTRICITY": [
            ("हमारे गांव में पिछले तीन महीने से बिजली नहीं आ रही है। ट्रांसफार्मर खराब है।", "There is no electricity in our village for the last three months. The transformer is broken.", "NEGATIVE"),
            ("रोज रात को 4 घंटे बिजली कट जाती है।", "Power is cut for 4 hours every night.", "NEGATIVE"),
            ("वोल्टेज बहुत कम आ रहा है, उपकरण जलने का डर है।", "Voltage is very low, afraid that appliances might burn.", "NEGATIVE")
        ],
        "HEALTHCARE": [
            ("सरकारी अस्पताल में डॉक्टर समय पर नहीं आते हैं।", "Doctors do not come on time at the government hospital.", "NEGATIVE"),
            ("दवाखाने में जरूरी दवाइयां खत्म हो गई हैं।", "Essential medicines are out of stock at the dispensary.", "NEGATIVE"),
            ("अस्पताल में साफ-सफाई बिल्कुल नहीं है।", "There is absolutely no cleanliness in the hospital.", "NEGATIVE")
        ],
        "EDUCATION": [
            ("प्राथमिक विद्यालय में छत से पानी टपकता है।", "Water leaks from the roof in the primary school.", "NEGATIVE"),
            ("स्कूल में शिक्षकों की कमी है, बच्चों की पढ़ाई खराब हो रही है।", "There is a shortage of teachers in the school, children's studies are suffering.", "NEGATIVE"),
            ("मिड-डे मील का खाना बहुत खराब गुणवत्ता का है।", "The mid-day meal food is of very poor quality.", "NEGATIVE")
        ],
        "SANITATION": [
            ("मोहल्ले में कचरे का ढेर लगा है, कोई उठाने नहीं आता।", "There is a pile of garbage in the neighborhood, no one comes to pick it up.", "NEGATIVE"),
            ("नालियां जाम हो गई हैं और गंदा पानी सड़क पर आ रहा है।", "Drains are clogged and dirty water is overflowing onto the road.", "NEGATIVE"),
            ("सार्वजनिक शौचालय की हालत बहुत खराब है।", "The condition of the public toilet is very bad.", "NEGATIVE")
        ],
        "DIGITAL": [
            ("कॉमन सर्विस सेंटर का इंटरनेट हमेशा बंद रहता है।", "The internet at the Common Service Center is always down.", "NEGATIVE"),
            ("गाँव में मोबाइल नेटवर्क बिल्कुल नहीं आता।", "There is no mobile network in the village at all.", "NEGATIVE"),
            ("सरकारी वेबसाइट काम नहीं कर रही है, फॉर्म नहीं भर पा रहे हैं।", "The government website is not working, cannot fill the form.", "NEGATIVE")
        ]
    },
    "Tamil": {
        "ROADS": [
            ("எங்கள் பகுதியில் சாலை மிகவும் மோசமாக உள்ளது, நிறைய குழிகள் உள்ளன.", "The road in our area is very bad, there are many potholes.", "NEGATIVE"),
            ("மழைக்கு பிறகு பிரதான சாலை சேதமடைந்துள்ளது, தயவுசெய்து சரிசெய்யவும்.", "The main road is damaged after the rain, please repair it.", "NEGATIVE"),
            ("சாலை போடும் பணி பாதியில் நிற்கிறது.", "Road laying work is stopped halfway.", "NEGATIVE")
        ],
        "WATER": [
            ("எங்கள் பகுதியில் கடந்த இரண்டு மாதமாக குடிநீர் வரவில்லை", "Drinking water hasn't come to our area for the last two months", "NEGATIVE"),
            ("குழாயில் வரும் தண்ணீர் மிகவும் அசுத்தமாக உள்ளது.", "The tap water is very dirty.", "NEGATIVE"),
            ("குடிநீர் தட்டுப்பாடு அதிகமாக உள்ளது, தண்ணீர் லாரி அனுப்பவும்.", "Drinking water scarcity is high, send a water lorry.", "NEGATIVE")
        ],
        "ELECTRICITY": [
            ("மின்மாற்றி பழுதாகி மூன்று நாட்கள் ஆகிறது, இன்னும் சரிசெய்யவில்லை.", "It has been three days since the transformer broke down, still not repaired.", "NEGATIVE"),
            ("அடிக்கடி மின்வெட்டு ஏற்படுகிறது.", "Frequent power cuts are happening.", "NEGATIVE"),
            ("குறைந்த மின்னழுத்தம் காரணமாக மின்சாதனங்கள் பழுதாகின்றன.", "Appliances are getting damaged due to low voltage.", "NEGATIVE")
        ],
        "HEALTHCARE": [
            ("அரசு மருத்துவமனையில் போதிய மருத்துவர்கள் இல்லை.", "There are not enough doctors in the government hospital.", "NEGATIVE"),
            ("ஆரம்ப சுகாதார நிலையத்தில் மருந்துகள் இல்லை.", "There are no medicines at the primary health centre.", "NEGATIVE"),
            ("மருத்துவமனையில் அடிப்படை வசதிகள் இல்லை.", "There are no basic facilities at the hospital.", "NEGATIVE")
        ],
        "EDUCATION": [
            ("அரசு பள்ளிக் கட்டிடம் மிகவும் பழுதடைந்துள்ளது.", "The government school building is heavily damaged.", "NEGATIVE"),
            ("பள்ளியில் போதுமான ஆசிரியர்கள் இல்லை.", "There are not enough teachers in the school.", "NEGATIVE"),
            ("மாணவர்களுக்கு குடிநீர் வசதி இல்லை.", "There is no drinking water facility for students.", "NEGATIVE")
        ],
        "SANITATION": [
            ("தெருவில் குப்பைகள் தேங்கி கிடக்கின்றன.", "Garbage is stagnating on the street.", "NEGATIVE"),
            ("சாக்கடை அடைத்து கழிவுநீர் சாலையில் வழிகிறது.", "Drain is blocked and sewage overflows on the road.", "NEGATIVE"),
            ("பொது கழிப்பறை சுத்தம் இல்லாமல் உள்ளது.", "Public toilet is unhygienic.", "NEGATIVE")
        ],
        "DIGITAL": [
            ("எங்கள் கிராமத்தில் செல்போன் டவர் இல்லை, சிக்னல் கிடைப்பதில்லை.", "There is no cell phone tower in our village, we don't get signal.", "NEGATIVE"),
            ("இ-சேவை மையத்தில் சர்வர் வேலை செய்யவில்லை.", "Server is not working at the e-Seva centre.", "NEGATIVE"),
            ("இணையதளம் மிகவும் மெதுவாக உள்ளது.", "Internet is very slow.", "NEGATIVE")
        ]
    },
    "Telugu": {
        "ROADS": [
            ("మా ఊరిలో రోడ్డు చాలా దారుణంగా ఉంది, గుంతలు పడ్డాయి.", "The road in our village is very bad, potholes have formed.", "NEGATIVE"),
            ("వర్షాలకు ప్రధాన రహదారి కొట్టుకుపోయింది.", "The main road washed away in the rains.", "NEGATIVE"),
            ("రోడ్డు విస్తరణ పనులు మధ్యలోనే ఆగిపోయాయి.", "Road expansion works stopped midway.", "NEGATIVE")
        ],
        "WATER": [
            ("మా కాలనీలో మూడు రోజులుగా మంచి నీరు రావడం లేదు.", "Drinking water has not been coming in our colony for three days.", "NEGATIVE"),
            ("నల్లా నీళ్లు చాలా మురికిగా వస్తున్నాయి.", "Tap water is coming very dirty.", "NEGATIVE"),
            ("వేసవిలో నీటి ఎద్దడి తీవ్రంగా ఉంది, ట్యాంకర్లు పంపండి.", "Water scarcity is severe in summer, send tankers.", "NEGATIVE")
        ],
        "ELECTRICITY": [
            ("ట్రాన్స్‌ఫార్మర్ కాలిపోయి వారం అవుతోంది, ఇంకా బాగుచేయలేదు.", "It's been a week since the transformer burnt out, not repaired yet.", "NEGATIVE"),
            ("ప్రతిరోజూ కరెంట్ కోతలు ఉంటున్నాయి.", "There are daily power cuts.", "NEGATIVE"),
            ("లో వోల్టేజ్ సమస్యతో మోటార్లు కాలిపోతున్నాయి.", "Motors are burning out due to low voltage problem.", "NEGATIVE")
        ],
        "HEALTHCARE": [
            ("ప్రభుత్వ ఆసుపత్రిలో డాక్టర్లు సరిగ్గా రావడం లేదు.", "Doctors are not coming properly to the government hospital.", "NEGATIVE"),
            ("ఆసుపత్రిలో కనీస మందులు లేవు.", "There are no basic medicines in the hospital.", "NEGATIVE"),
            ("ప్రాథమిక ఆరోగ్య కేంద్రం ఎప్పుడూ మూసే ఉంటుంది.", "The primary health centre is always closed.", "NEGATIVE")
        ],
        "EDUCATION": [
            ("బడిలో పైకప్పు పెచ్చులూడి పడుతోంది.", "The ceiling in the school is flaking and falling.", "NEGATIVE"),
            ("పిల్లలకు సరిపడా టీచర్లు లేరు.", "There are not enough teachers for the children.", "NEGATIVE"),
            ("మధ్యాహ్న భోజనం నాణ్యత బాగోలేదు.", "Mid-day meal quality is not good.", "NEGATIVE")
        ],
        "SANITATION": [
            ("చెత్త తీసుకెళ్లే బండి వారానికోసారి వస్తోంది.", "The garbage truck comes once a week.", "NEGATIVE"),
            ("డ్రైనేజీ పొంగి రోడ్డు మీదకు వస్తోంది.", "Drainage is overflowing onto the road.", "NEGATIVE"),
            ("పారిశుధ్య కార్మికులు వీధులు ఊడ్చడం లేదు.", "Sanitation workers are not sweeping the streets.", "NEGATIVE")
        ],
        "DIGITAL": [
            ("మా ఊళ్లో ఇంటర్నెట్ సిగ్నల్ అస్సలు రావడం లేదు.", "Internet signal doesn't come at all in our village.", "NEGATIVE"),
            ("మీసేవ కేంద్రంలో నెట్వర్క్ లేదు అంటున్నారు.", "They say there is no network at the MeeSeva center.", "NEGATIVE"),
            ("ఆన్లైన్ దరఖాస్తు వెబ్సైట్ పనిచేయడం లేదు.", "Online application website is not working.", "NEGATIVE")
        ]
    },
    "Kannada": {
        "ROADS": [
            ("ನಮ್ಮ ರಸ್ತೆಯಲ್ಲಿ ತುಂಬಾ ಗುಂಡಿಗಳಿವೆ, ವಾಹನ ಚಲಾಯಿಸಲು ಕಷ್ಟ.", "There are many potholes on our road, difficult to drive.", "NEGATIVE"),
            ("ಮಳೆಯಿಂದ ರಸ್ತೆ ಸಂಪೂರ್ಣ ಹಾಳಾಗಿದೆ.", "Road is completely damaged due to rain.", "NEGATIVE"),
            ("ರಸ್ತೆ ಕಾಮಗಾರಿ ಅಪೂರ್ಣವಾಗಿದೆ.", "Road work is incomplete.", "NEGATIVE")
        ],
        "WATER": [
            ("ನಾಲ್ಕು ದಿನಗಳಿಂದ ಕುಡಿಯುವ ನೀರು ಬಂದಿಲ್ಲ.", "Drinking water hasn't come for four days.", "NEGATIVE"),
            ("ನೀರು ಕಲುಷಿತವಾಗಿದೆ, ಕುಡಿಯಲು ಯೋಗ್ಯವಾಗಿಲ್ಲ.", "Water is polluted, not fit for drinking.", "NEGATIVE"),
            ("ನೀರಿನ ಪೈಪ್ ಒಡೆದು ನೀರು ಪೋಲಾಗುತ್ತಿದೆ.", "Water pipe is broken and water is wasting.", "NEGATIVE")
        ],
        "ELECTRICITY": [
            ("ಪದೇ ಪದೇ ವಿದ್ಯುತ್ ಕಡಿತಗೊಳ್ಳುತ್ತಿದೆ.", "Frequent power cuts are happening.", "NEGATIVE"),
            ("ಟ್ರಾನ್ಸ್‌ಫಾರ್ಮರ್ ಸುಟ್ಟುಹೋಗಿದೆ, ದಯವಿಟ್ಟು ಸರಿಪಡಿಸಿ.", "Transformer has burnt, please fix it.", "NEGATIVE"),
            ("ಕಡಿಮೆ ವೋಲ್ಟೇಜ್‌ನಿಂದ ಉಪಕರಣಗಳು ಹಾಳಾಗುತ್ತಿವೆ.", "Appliances are getting damaged due to low voltage.", "NEGATIVE")
        ],
        "HEALTHCARE": [
            ("ಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆಯಲ್ಲಿ ವೈದ್ಯರಿಲ್ಲ.", "There are no doctors in the government hospital.", "NEGATIVE"),
            ("ಆಸ್ಪತ್ರೆಯಲ್ಲಿ ಔಷಧಿಗಳ ಕೊರತೆ ಇದೆ.", "There is a shortage of medicines in the hospital.", "NEGATIVE"),
            ("ತುರ್ತು ಚಿಕಿತ್ಸಾ ಘಟಕ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತಿಲ್ಲ.", "Emergency unit is not functioning.", "NEGATIVE")
        ],
        "EDUCATION": [
            ("ಶಾಲಾ ಕಟ್ಟಡ ದುರಸ್ತಿಯಲ್ಲಿದೆ.", "School building is under disrepair.", "NEGATIVE"),
            ("ಮಕ್ಕಳಿಗೆ ಕುಳಿತುಕೊಳ್ಳಲು ಬೆಂಚ್‌ಗಳಿಲ್ಲ.", "There are no benches for children to sit.", "NEGATIVE"),
            ("ಶಾಲೆಯಲ್ಲಿ ಶೌಚಾಲಯದ ವ್ಯವಸ್ಥೆ ಇಲ್ಲ.", "There is no toilet facility in the school.", "NEGATIVE")
        ],
        "SANITATION": [
            ("ಚರಂಡಿ ಕಟ್ಟಿಕೊಂಡಿದ್ದು, ಕೊಳಚೆ ನೀರು ರಸ್ತೆಗೆ ಹರಿಯುತ್ತಿದೆ.", "Drain is clogged, sewage water is flowing onto the road.", "NEGATIVE"),
            ("ಕಸ ವಿಲೇವಾರಿ ಸರಿಯಾಗಿ ಆಗುತ್ತಿಲ್ಲ.", "Garbage disposal is not happening properly.", "NEGATIVE"),
            ("ಸಾರ್ವಜನಿಕ ಶೌಚಾಲಯ ಸ್ವಚ್ಛವಾಗಿಲ್ಲ.", "Public toilet is not clean.", "NEGATIVE")
        ],
        "DIGITAL": [
            ("ಗ್ರಾಮ ಪಂಚಾಯತಿಯಲ್ಲಿ ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕವಿಲ್ಲ.", "No internet connection in Gram Panchayat.", "NEGATIVE"),
            ("ಮೊಬೈಲ್ ನೆಟ್‌ವರ್ಕ್ ಸಮಸ್ಯೆ ತುಂಬಾ ಇದೆ.", "Mobile network problem is severe.", "NEGATIVE"),
            ("ಆನ್‌ಲೈನ್ ಪೋರ್ಟಲ್ ಸರ್ವರ್ ಡೌನ್ ಆಗಿದೆ.", "Online portal server is down.", "NEGATIVE")
        ]
    },
    "Marathi": {
        "ROADS": [
            ("आमच्या भागात रस्त्याची अवस्था खूप वाईट आहे, अनेक खड्डे आहेत.", "The condition of the road in our area is very bad, there are many potholes.", "NEGATIVE"),
            ("पावसामुळे रस्ता पूर्णपणे वाहून गेला आहे.", "The road has completely washed away due to rain.", "NEGATIVE"),
            ("रस्त्याचे काम अर्धवट सोडले आहे.", "The road work is left halfway.", "NEGATIVE")
        ],
        "WATER": [
            ("गेल्या चार दिवसांपासून नळाला पाणी नाही.", "There is no water in the tap for the last four days.", "NEGATIVE"),
            ("पिण्याचे पाणी गढूळ येत आहे.", "Drinking water is coming muddy.", "NEGATIVE"),
            ("पाण्याची पाइपलाइन फुटली आहे.", "Water pipeline is broken.", "NEGATIVE")
        ],
        "ELECTRICITY": [
            ("गावात सारखी वीज जाते, खूप त्रास होत आहे.", "Power goes out frequently in the village, causing a lot of trouble.", "NEGATIVE"),
            ("ट्रान्सफॉर्मर बिघडला आहे, त्वरित दुरुस्त करा.", "Transformer is faulty, repair it immediately.", "NEGATIVE"),
            ("कमी दाबाने वीजपुरवठा होत आहे.", "Power supply is at low voltage.", "NEGATIVE")
        ],
        "HEALTHCARE": [
            ("सरकारी रुग्णालयात डॉक्टर उपलब्ध नसतात.", "Doctors are not available in the government hospital.", "NEGATIVE"),
            ("दवाखान्यात आवश्यक औषधे मिळत नाहीत.", "Essential medicines are not available in the clinic.", "NEGATIVE"),
            ("रुग्णवाहिका वेळेवर पोहचत नाही.", "Ambulance does not arrive on time.", "NEGATIVE")
        ],
        "EDUCATION": [
            ("जिल्हा परिषदेच्या शाळेची इमारत मोडकळीस आली आहे.", "The Zilla Parishad school building is dilapidated.", "NEGATIVE"),
            ("शाळेत शिक्षकांची कमतरता आहे.", "There is a shortage of teachers in the school.", "NEGATIVE"),
            ("शालेय पोषण आहार चांगल्या दर्जाचा नाही.", "School nutrition meal is not of good quality.", "NEGATIVE")
        ],
        "SANITATION": [
            ("कचरा कुंडी भरून वाहत आहे, कोणी साफ करत नाही.", "Garbage bin is overflowing, no one cleans it.", "NEGATIVE"),
            ("गटारे तुंबली आहेत आणि पाणी रस्त्यावर येत आहे.", "Gutters are clogged and water is coming on the road.", "NEGATIVE"),
            ("सार्वजनिक स्वच्छतागृहात खूप घाण आहे.", "There is a lot of dirt in the public toilet.", "NEGATIVE")
        ],
        "DIGITAL": [
            ("महा ई-सेवा केंद्रात इंटरनेट चालत नाही.", "Internet does not work in Maha e-Seva center.", "NEGATIVE"),
            ("गावात मोबाईल नेटवर्कची खूप समस्या आहे.", "There is a huge problem of mobile network in the village.", "NEGATIVE"),
            ("शासकीय वेबसाइट उघडत नाही.", "Government website does not open.", "NEGATIVE")
        ]
    },
    "Gujarati": {
        "ROADS": [
            ("અમારા વિસ્તારમાં રસ્તામાં મોટા ખાડા પડી ગયા છે.", "Large potholes have formed on the road in our area.", "NEGATIVE"),
            ("ચોમાસામાં રસ્તો તૂટી ગયો છે, રિપેરિંગની જરૂર છે.", "The road broke during monsoon, needs repairing.", "NEGATIVE"),
            ("રસ્તાનું કામ ગોકળગાયની ગતિએ ચાલી રહ્યું છે.", "Road work is going at a snail's pace.", "NEGATIVE")
        ],
        "WATER": [
            ("અમારા વોર્ડમાં પાણી પૂરતા પ્રમાણમાં આવતું નથી.", "Water does not come in sufficient quantity in our ward.", "NEGATIVE"),
            ("પીવાનું પાણી ગંદુ અને દુર્ગંધવાળું આવી રહ્યું છે.", "Drinking water is coming dirty and smelly.", "NEGATIVE"),
            ("ઉનાળામાં પાણીની મોટી સમસ્યા છે, ટેન્કર મોકલો.", "There is a major water problem in summer, send a tanker.", "NEGATIVE")
        ],
        "ELECTRICITY": [
            ("ટ્રાન્સફોર્મર બળી ગયું છે, ક્યારે બદલશો?", "Transformer has burnt, when will you change it?", "NEGATIVE"),
            ("વારંવાર પાવર કટ થાય છે.", "Frequent power cuts occur.", "NEGATIVE"),
            ("ખેતી માટે પૂરતી વીજળી મળતી નથી.", "Not getting enough electricity for farming.", "NEGATIVE")
        ],
        "HEALTHCARE": [
            ("સરકારી દવાખાનામાં ડોક્ટર સમયસર આવતા નથી.", "Doctors do not come on time at the government clinic.", "NEGATIVE"),
            ("હોસ્પિટલમાં દવાઓનો સ્ટોક નથી.", "There is no stock of medicines in the hospital.", "NEGATIVE"),
            ("દર્દીઓ માટે પૂરતા બેડ નથી.", "Not enough beds for patients.", "NEGATIVE")
        ],
        "EDUCATION": [
            ("પ્રાથમિક શાળાની છતમાંથી પાણી ટપકે છે.", "Water leaks from the roof of the primary school.", "NEGATIVE"),
            ("શાળામાં પૂરતા શિક્ષકો નથી.", "Not enough teachers in the school.", "NEGATIVE"),
            ("બાળકો માટે પીવાના પાણીની સુવિધા નથી.", "No drinking water facility for children.", "NEGATIVE")
        ],
        "SANITATION": [
            ("ગટર લાઈન બ્લોક થઈ ગઈ છે.", "Drainage line has blocked.", "NEGATIVE"),
            ("કચરાની ગાડી નિયમિત આવતી નથી.", "Garbage van does not come regularly.", "NEGATIVE"),
            ("શેરીઓમાં સફાઈ થતી નથી.", "Cleaning is not done in the streets.", "NEGATIVE")
        ],
        "DIGITAL": [
            ("ગામમાં ઈન્ટરનેટ કનેક્ટિવિટી નથી.", "No internet connectivity in the village.", "NEGATIVE"),
            ("પંચાયતમાં ઈન્ટરનેટ ચાલતું નથી.", "Internet does not work in the panchayat.", "NEGATIVE"),
            ("ઓનલાઈન પોર્ટલ બહુ ધીમું ચાલે છે.", "Online portal runs very slow.", "NEGATIVE")
        ]
    },
    "Bengali": {
        "ROADS": [
            ("রাস্তার অবস্থা খুব খারাপ, বড় বড় গর্ত হয়ে গেছে।", "The condition of the road is very bad, big potholes have formed.", "NEGATIVE"),
            ("বৃষ্টির পর রাস্তা চলাচলের অযোগ্য হয়ে পড়েছে।", "The road has become unnavigable after rain.", "NEGATIVE"),
            ("রাস্তা মেরামতের কাজ মাঝপথেই বন্ধ।", "Road repair work stopped midway.", "NEGATIVE")
        ],
        "WATER": [
            ("কল থেকে ঘোলা জল বেরোচ্ছে, পান করার অযোগ্য।", "Muddy water is coming from the tap, unfit for drinking.", "NEGATIVE"),
            ("গত তিনদিন ধরে জলের সাপ্লাই নেই।", "No water supply for the last three days.", "NEGATIVE"),
            ("পানীয় জলের তীব্র সংকট দেখা দিয়েছে।", "A severe crisis of drinking water has appeared.", "NEGATIVE")
        ],
        "ELECTRICITY": [
            ("ট্রান্সফর্মার খারাপ, সারা গ্রাম অন্ধকারে।", "Transformer is broken, entire village in darkness.", "NEGATIVE"),
            ("লো-ভোল্টেজের কারণে ইলেকট্রনিক জিনিসপত্র নষ্ট হচ্ছে।", "Electronic items are getting ruined due to low voltage.", "NEGATIVE"),
            ("ঘন ঘন কারেন্ট চলে যাচ্ছে।", "Frequent power cuts are happening.", "NEGATIVE")
        ],
        "HEALTHCARE": [
            ("হাসপাতালে ডাক্তার থাকে না।", "Doctors are not present in the hospital.", "NEGATIVE"),
            ("ওষুধের দোকানে জরুরি ওষুধ নেই।", "Emergency medicines are not in the pharmacy.", "NEGATIVE"),
            ("হাসপাতালের পরিবেশ খুব নোংরা।", "The hospital environment is very dirty.", "NEGATIVE")
        ],
        "EDUCATION": [
            ("স্কুলের ভবনের অবস্থা বিপজ্জনক।", "The condition of the school building is dangerous.", "NEGATIVE"),
            ("স্কুলে শিক্ষকের অভাব রয়েছে।", "There is a lack of teachers in the school.", "NEGATIVE"),
            ("মিড-ডে মিলের খাবার অত্যন্ত খারাপ মানের।", "Mid-day meal food is of extremely poor quality.", "NEGATIVE")
        ],
        "SANITATION": [
            ("ড্রেন উপচে নোংরা জল রাস্তায় আসছে।", "Dirty water overflowing from the drain is coming onto the road.", "NEGATIVE"),
            ("পাড়ায় আবর্জনার স্তূপ জমে আছে।", "Pile of garbage is accumulated in the neighborhood.", "NEGATIVE"),
            ("পাবলিক টয়লেটের অবস্থা শোচনীয়।", "Condition of public toilet is pathetic.", "NEGATIVE")
        ],
        "DIGITAL": [
            ("আমাদের গ্রামে ইন্টারনেটের স্পিড খুব কম।", "Internet speed in our village is very slow.", "NEGATIVE"),
            ("কমন সার্ভিস সেন্টারে সার্ভার ডাউন।", "Server down at the Common Service Center.", "NEGATIVE"),
            ("সরকারি পোর্টাল খুলছে না।", "Government portal is not opening.", "NEGATIVE")
        ]
    },
    "Malayalam": {
        "ROADS": [
            ("ഞങ്ങളുടെ പ്രദേശത്തെ റോഡ് വളരെ മോശമാണ്, ധാരാളം കുഴികളുണ്ട്.", "The road in our area is very bad, there are many potholes.", "NEGATIVE"),
            ("മഴക്കാലത്ത് റോഡ് പൂർണ്ണമായും തകർന്നു.", "The road was completely destroyed during the rainy season.", "NEGATIVE"),
            ("റോഡ് പണി പകുതിവഴിയിൽ നിർത്തിവച്ചു.", "Road work was stopped halfway.", "NEGATIVE")
        ],
        "WATER": [
            ("രണ്ട് ദിവസമായി കുടിവെള്ളം ലഭിക്കുന്നില്ല.", "Drinking water is not available for two days.", "NEGATIVE"),
            ("പൈപ്പിൽ നിന്ന് വരുന്ന വെള്ളം വളരെ മലിനമാണ്.", "The water coming from the pipe is very polluted.", "NEGATIVE"),
            ("വേനൽക്കാലത്ത് കടുത്ത ജലക്ഷാമം അനുഭവപ്പെടുന്നു.", "Severe water shortage is felt during summer.", "NEGATIVE")
        ],
        "ELECTRICITY": [
            ("ട്രാൻസ്ഫോർമർ കേടായിട്ട് ദിവസങ്ങളായി.", "It has been days since the transformer broke down.", "NEGATIVE"),
            ("പലപ്പോഴും വൈദ്യുതി തടസ്സം ഉണ്ടാകുന്നു.", "Power outages happen frequently.", "NEGATIVE"),
            ("ലോ വോൾട്ടേജ് കാരണം ഉപകരണങ്ങൾ നശിക്കുന്നു.", "Appliances are destroyed due to low voltage.", "NEGATIVE")
        ],
        "HEALTHCARE": [
            ("സർക്കാർ ആശുപത്രിയിൽ ഡോക്ടർമാരില്ല.", "There are no doctors in the government hospital.", "NEGATIVE"),
            ("ആവശ്യത്തിന് മരുന്നുകൾ ലഭ്യമല്ല.", "Enough medicines are not available.", "NEGATIVE"),
            ("ആശുപത്രിയിൽ ശുചിത്വമില്ല.", "There is no cleanliness in the hospital.", "NEGATIVE")
        ],
        "EDUCATION": [
            ("സ്കൂൾ കെട്ടിടം ചോർന്നൊലിക്കുന്നു.", "The school building is leaking.", "NEGATIVE"),
            ("സ്കൂളിൽ അധ്യാപകരുടെ കുറവുണ്ട്.", "There is a shortage of teachers in the school.", "NEGATIVE"),
            ("കുട്ടികൾക്ക് കുടിവെള്ള സൗകര്യമില്ല.", "There is no drinking water facility for children.", "NEGATIVE")
        ],
        "SANITATION": [
            ("മാലിന്യം കൃത്യമായി ശേഖരിക്കുന്നില്ല.", "Garbage is not collected properly.", "NEGATIVE"),
            ("ഓടകൾ അടഞ്ഞ് വെള്ളം റോഡിലേക്ക് ഒഴുകുന്നു.", "Drains are clogged and water overflows onto the road.", "NEGATIVE"),
            ("പൊതു ശൗചാലയം ഉപയോഗശൂന്യമാണ്.", "The public toilet is useless.", "NEGATIVE")
        ],
        "DIGITAL": [
            ("അക്ഷയ കേന്ദ്രത്തിൽ ഇന്റർനെറ്റ് ഇല്ല.", "There is no internet at the Akshaya Center.", "NEGATIVE"),
            ("മൊബൈൽ നെറ്റ്‌വർക്ക് വളരെ മോശമാണ്.", "Mobile network is very bad.", "NEGATIVE"),
            ("ഓൺലൈൻ സേവനങ്ങൾ തടസ്സപ്പെടുന്നു.", "Online services are interrupted.", "NEGATIVE")
        ]
    },
    "Odia": {
        "ROADS": [
            ("ଆମ ଅଞ୍ଚଳର ରାସ୍ତା ବହୁତ ଖରାପ, ଅନେକ ଖାଲ ଅଛି |", "The road in our area is very bad, there are many potholes.", "NEGATIVE"),
            ("ବର୍ଷା ଯୋଗୁଁ ରାସ୍ତା ଧୋଇ ହୋଇଯାଇଛି |", "The road has washed away due to rain.", "NEGATIVE"),
            ("ରାସ୍ତା କାମ ଅଧାରେ ଅଟକି ରହିଛି |", "Road work is stuck halfway.", "NEGATIVE")
        ],
        "WATER": [
            ("ତିନି ଦିନ ହେଲା ପିଇବା ପାଣି ଆସୁନାହିଁ |", "Drinking water is not coming for three days.", "NEGATIVE"),
            ("ପାଣି ପାଇପ୍ ଫାଟି ଯାଇଛି |", "Water pipe has burst.", "NEGATIVE"),
            ("ଟ୍ୟାପରୁ ଅପରିଷ୍କାର ପାଣି ବାହାରୁଛି |", "Dirty water is coming out of the tap.", "NEGATIVE")
        ],
        "ELECTRICITY": [
            ("ଟ୍ରାନ୍ସଫର୍ମର ପୋଡି ଯାଇଛି, ଦୟାକରି ଠିକ୍ କରନ୍ତୁ |", "Transformer has burnt, please fix it.", "NEGATIVE"),
            ("ବାରମ୍ବାର ବିଦ୍ୟୁତ୍ କାଟ ହେଉଛି |", "Frequent power cuts are happening.", "NEGATIVE"),
            ("ଲୋ-ଭୋଲଟେଜ୍ ଯୋଗୁଁ ଲାଇଟ୍ ଜଳୁନାହିଁ |", "Lights are not turning on due to low voltage.", "NEGATIVE")
        ],
        "HEALTHCARE": [
            ("ଡାକ୍ତରଖାନାରେ ଡାକ୍ତର ନାହାଁନ୍ତି |", "There are no doctors in the hospital.", "NEGATIVE"),
            ("ଔଷଧ ଦୋକାନରେ ଔଷଧ ନାହିଁ |", "There is no medicine in the pharmacy.", "NEGATIVE"),
            ("ଆମ୍ବୁଲାନ୍ସ ଠିକ୍ ସମୟରେ ପହଞ୍ଚୁ ନାହିଁ |", "Ambulance is not arriving on time.", "NEGATIVE")
        ],
        "EDUCATION": [
            ("ବିଦ୍ୟାଳୟ ଘରର ଅବସ୍ଥା ଭଲ ନାହିଁ |", "The condition of the school building is not good.", "NEGATIVE"),
            ("ସ୍କୁଲରେ ଶିକ୍ଷକଙ୍କ ଅଭାବ ଅଛି |", "There is a shortage of teachers in the school.", "NEGATIVE"),
            ("ମଧ୍ୟାହ୍ନ ଭୋଜନ ନିମ୍ନ ମାନର |", "Mid-day meal is of low quality.", "NEGATIVE")
        ],
        "SANITATION": [
            ("ଡ୍ରେନ୍ ଜାମ୍ ହୋଇ ରାସ୍ତା ଉପରକୁ ପାଣି ଆସୁଛି |", "Drain is jammed and water is coming onto the road.", "NEGATIVE"),
            ("ଅଳିଆ ଆବର୍ଜନା ଉଠାଯାଉ ନାହିଁ |", "Garbage is not being picked up.", "NEGATIVE"),
            ("ସର୍ବସାଧାରଣ ଶୌଚାଳୟ ଅପରିଷ୍କାର |", "Public toilet is unhygienic.", "NEGATIVE")
        ],
        "DIGITAL": [
            ("ଗାଁରେ ଇଣ୍ଟରନେଟ୍ କାମ କରୁନାହିଁ |", "Internet is not working in the village.", "NEGATIVE"),
            ("ମୋବାଇଲ୍ ନେଟୱାର୍କ ସମସ୍ୟା ଅଛି |", "There is a mobile network problem.", "NEGATIVE"),
            ("ସରକାରୀ ୱେବସାଇଟ୍ ଖୋଲୁନାହିଁ |", "Government website is not opening.", "NEGATIVE")
        ]
    },
    "Punjabi": {
        "ROADS": [
            ("ਸਾਡੇ ਇਲਾਕੇ ਦੀ ਸੜਕ ਬਹੁਤ ਟੁੱਟੀ ਹੋਈ ਹੈ।", "The road in our area is very broken.", "NEGATIVE"),
            ("ਮੀਂਹ ਕਰਕੇ ਸੜਕ ਤੇ ਵੱਡੇ ਟੋਏ ਪੈ ਗਏ ਹਨ।", "Big potholes have formed on the road due to rain.", "NEGATIVE"),
            ("ਨਵੀਂ ਸੜਕ ਬਣਾਉਣ ਦਾ ਕੰਮ ਵਿੱਚ ਹੀ ਰੁਕਿਆ ਹੋਇਆ ਹੈ।", "The work of building the new road is stopped in the middle.", "NEGATIVE")
        ],
        "WATER": [
            ("ਨਲਕੇ ਵਿੱਚ ਪਾਣੀ ਬਹੁਤ ਗੰਦਾ ਆ ਰਿਹਾ ਹੈ।", "Very dirty water is coming in the tap.", "NEGATIVE"),
            ("ਪਿਛਲੇ ਦੋ ਦਿਨਾਂ ਤੋਂ ਪਾਣੀ ਦੀ ਸਪਲਾਈ ਬੰਦ ਹੈ।", "Water supply is closed for the last two days.", "NEGATIVE"),
            ("ਗਰਮੀਆਂ ਵਿੱਚ ਪੀਣ ਵਾਲੇ ਪਾਣੀ ਦੀ ਬਹੁਤ ਕਿੱਲਤ ਹੈ।", "There is a huge shortage of drinking water in summer.", "NEGATIVE")
        ],
        "ELECTRICITY": [
            ("ਟਰਾਂਸਫਾਰਮਰ ਖਰਾਬ ਹੈ, ਸਾਰਾ ਪਿੰਡ ਹਨੇਰੇ ਵਿੱਚ ਹੈ।", "Transformer is faulty, entire village is in darkness.", "NEGATIVE"),
            ("ਬਿਜਲੀ ਦਾ ਬਹੁਤ ਲੰਮਾ ਕੱਟ ਲੱਗਦਾ ਹੈ।", "There is a very long power cut.", "NEGATIVE"),
            ("ਵੋਲਟੇਜ ਬਹੁਤ ਘੱਟ ਆ ਰਹੀ ਹੈ।", "Voltage is coming very low.", "NEGATIVE")
        ],
        "HEALTHCARE": [
            ("ਸਰਕਾਰੀ ਹਸਪਤਾਲ ਵਿੱਚ ਡਾਕਟਰ ਡਿਊਟੀ ਤੇ ਨਹੀਂ ਹੁੰਦੇ।", "Doctors are not on duty at the government hospital.", "NEGATIVE"),
            ("ਹਸਪਤਾਲ ਵਿੱਚ ਦਵਾਈਆਂ ਨਹੀਂ ਮਿਲਦੀਆਂ।", "Medicines are not available in the hospital.", "NEGATIVE"),
            ("ਮਰੀਜ਼ਾਂ ਲਈ ਬੈੱਡ ਘੱਟ ਹਨ।", "Beds are less for patients.", "NEGATIVE")
        ],
        "EDUCATION": [
            ("ਸਕੂਲ ਦੀ ਇਮਾਰਤ ਦੀ ਹਾਲਤ ਬਹੁਤ ਖਸਤਾ ਹੈ।", "The condition of the school building is very poor.", "NEGATIVE"),
            ("ਸਕੂਲ ਵਿੱਚ ਅਧਿਆਪਕਾਂ ਦੀ ਘਾਟ ਹੈ।", "There is a shortage of teachers in the school.", "NEGATIVE"),
            ("ਬੱਚਿਆਂ ਲਈ ਪੀਣ ਵਾਲਾ ਸਾਫ਼ ਪਾਣੀ ਨਹੀਂ ਹੈ।", "There is no clean drinking water for children.", "NEGATIVE")
        ],
        "SANITATION": [
            ("ਗਲੀਆਂ ਵਿੱਚ ਕੂੜੇ ਦੇ ਢੇਰ ਲੱਗੇ ਹੋਏ ਹਨ।", "Piles of garbage are gathered in the streets.", "NEGATIVE"),
            ("ਨਾਲੀਆਂ ਜਾਮ ਹਨ ਅਤੇ ਗੰਦਾ ਪਾਣੀ ਬਾਹਰ ਆ ਰਿਹਾ ਹੈ।", "Drains are jammed and dirty water is coming out.", "NEGATIVE"),
            ("ਪਿੰਡ ਵਿੱਚ ਸਫਾਈ ਦਾ ਕੋਈ ਪ੍ਰਬੰਧ ਨਹੀਂ ਹੈ।", "There is no arrangement for cleanliness in the village.", "NEGATIVE")
        ],
        "DIGITAL": [
            ("ਸੁਵਿਧਾ ਕੇਂਦਰ ਵਿੱਚ ਇੰਟਰਨੈੱਟ ਕੰਮ ਨਹੀਂ ਕਰਦਾ।", "Internet does not work in the Suvidha Center.", "NEGATIVE"),
            ("ਮੋਬਾਈਲ ਦਾ ਨੈੱਟਵਰਕ ਬਿਲਕੁਲ ਨਹੀਂ ਆਉਂਦਾ।", "Mobile network does not come at all.", "NEGATIVE"),
            ("ਆਨਲਾਈਨ ਫਾਰਮ ਭਰਨ ਵਿੱਚ ਦਿੱਕਤ ਆ ਰਹੀ ਹੈ।", "Facing difficulty in filling online forms.", "NEGATIVE")
        ]
    }
}

requests = []

sources = ["TELEGRAM", "WHATSAPP", "SMS", "WEBSITE", "APP"]

for i in range(1, NUM_REQUESTS + 1):
    district_info = random.choice(districts)
    district_name = district_info['district_name']
    state = district_info['state']
    lat = float(district_info['latitude']) + random.uniform(-0.05, 0.05)
    lon = float(district_info['longitude']) + random.uniform(-0.05, 0.05)
    
    # Determine language based on state, default to Hindi if state not mapped perfectly (though our data maps all states)
    lang = STATE_LANGUAGE_MAP.get(state, "Hindi")
    
    # Fallback to Hindi if somehow language templates are missing
    if lang not in TEMPLATES:
        lang = "Hindi"
        
    category = random.choice(CATEGORIES)
    templates = TEMPLATES[lang][category]
    template = random.choice(templates)
    
    raw_text = template[0]
    translated_text = template[1]
    sentiment = template[2]
    
    urgency = random.randint(1, 5)
    timestamp = random_date().strftime("%Y-%m-%dT%H:%M:%SZ")
    source = random.choice(sources)
    
    req_id = f"SYN-{str(i).zfill(5)}"
    
    request = {
        "id": req_id,
        "raw_text": raw_text,
        "translated_text": translated_text,
        "language_detected": lang,
        "category": category,
        "location_district": district_name,
        "location_state": state,
        "urgency": urgency,
        "sentiment": sentiment,
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "timestamp": timestamp,
        "source": source,
        "data_type": "SYNTHETIC"
    }
    requests.append(request)

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(requests, f, ensure_ascii=False, indent=2)

print(f"Generated {NUM_REQUESTS} synthetic requests in {OUTPUT_FILE}")
