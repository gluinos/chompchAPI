import pandas as pd
import numpy as np
from tqdm import tqdm
import json
import string
from ast import literal_eval

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer

from utils import clean_data


# pd.set_option('display.expand_frame_repr', False)

# metacategories = [
#     ["Coffee & Tea", "Fast Food", "Specialty Food", "Sandwiches", "Bakeries", "Cafes", "Delis",],
#     ["Salad","Vegetarian", "Breakfast & Brunch",],
#     ["Nightlife", "Wine & Spirits", "Beer", "Bars", "Breweries", "Wine Bars", "Pubs", "Sports Bars", "Cocktail",],
#     ["Mexican", "Latin American", "Tapas/Small Plates", "Tacos","Tex-Mex", ],
#     ["American (Traditional)", "American (New)", "Hot Dogs", "Burgers", "Diners", ],
#     ["Barbeque", "Southern", "Hawaiian", "Pizza", "Soup", "Diners", ],
#     ["Chicken Wings", "Health Markets", "Bagels", "Seafood", "Seafood Markets", "Butcher", "Cheese Shops", "Steakhouses", "Coffee",],
#     ["Ethnic Food", "Italian", "French", "Greek"], 
#     ["Asian Fusion", "Chinese", "Noodles", "Ramen", "Korean", "Taiwanese", "Sushi Bars", "Japanese", "Bubble Tea", "Vietnamese", "Poke", "Thai",],
#     ["Indian", "Thai", "Pakistani", ],
#     ["Desserts", "Ice Cream & Frozen Yogurt", "Candy Stores", "Donuts", "Shaved Ice", "Gelato", "Delicatessen", "Creperies", "Pancakes", "Waffles" ],
# ]
metacategories = [
    ["Breakfast & Brunch","American (Traditional)","Coffee & Tea","Cafes","Sandwiches","Diners","Canadian (New)","Middle Eastern","Burgers","American (New)","Barbeque","Mediterranean","Specialty Food","Ethnic Food","Steakhouses","Chinese","Salad","Bagels","Greek","Bakeries"],
    ["Pizza","Italian","Bakeries","Greek","Mediterranean","Chinese","Cafes","Sandwiches","Thai","Breakfast & Brunch","French","Mexican","Indian","Vegetarian","Asian Fusion","Halal","American (New)","Coffee & Tea","Hot Dogs","Seafood"],
    ["Nightlife","Bars","Event Planning & Services","Caterers","American (Traditional)","Italian","Pizza","Wine Bars","Breakfast & Brunch","Pubs","Venues & Event Spaces","Beer","Wine & Spirits","American (New)","Salad","Specialty Food","Seafood","Steakhouses","Mexican","Cafes"],
    ["Fast Food","Burgers","Coffee & Tea","American (Traditional)","Chicken Wings","Ice Cream & Frozen Yogurt","Chicken Shop","Buffets","Barbeque","American (New)","Asian Fusion","Breakfast & Brunch","Sandwiches","Chinese","Desserts","Korean","Seafood","Gluten-Free","Diners","Donuts"],
    ["Sandwiches","Pizza","Italian","Salad","Chicken Wings","Breakfast & Brunch","Coffee & Tea","American (New)","Cafes","Specialty Food","American (Traditional)","Juice Bars & Smoothies","Bakeries","Delis","Soup","Bagels","Gluten-Free","Fast Food","Asian Fusion","Food Delivery Services"],
    ["Nightlife","Bars","American (Traditional)","Sports Bars","Chicken Wings","Fast Food","Burgers","American (New)","Breakfast & Brunch","Arts & Entertainment","Seafood","Asian Fusion","Sandwiches","Desserts","Cocktail Bars","Coffee & Tea","Pubs","Steakhouses","Barbeque","Gluten-Free"],
    ["Mexican","Indian","Burgers","Thai","Japanese","Steakhouses","Diners","Hot Dogs","Latin American","Tex-Mex","Chinese","Pakistani","Dim Sum","Portuguese","Vegan","Vegetarian","Peruvian","Hawaiian","Tacos","Cafes"],
    ["Fast Food","Burgers","Vietnamese","Chinese","Seafood","American (Traditional)","Korean","Mexican","Buffets","Diners","Chicken Wings","Asian Fusion","Middle Eastern","Barbeque","Mediterranean","American (New)","Breakfast & Brunch","Hot Dogs","Canadian (New)","Coffee & Tea"],
    ["Nightlife","Bars","American (Traditional)","Event Planning & Services","American (New)","Beer","Wine & Spirits","Breakfast & Brunch","Sports Bars","Pizza","Sandwiches","Caterers","Pubs","Venues & Event Spaces","Arts & Entertainment","Italian","Cocktail Bars","Burgers","Salad","Wine Bars"],
    ["Japanese","Sushi Bars","Nightlife","Bars","Mexican","American (Traditional)","Tex-Mex","Fast Food","Steakhouses","Latin American","Chinese","Event Planning & Services","Vegetarian","Seafood","Ramen","Korean","Asian Fusion","Vegan","Burgers","Desserts"],
    ["Sandwiches","Fast Food","Delis","American (New)","Salad","Coffee & Tea","Soup","Burgers","Seafood","Cafes","Nightlife","Pizza","Asian Fusion","Vietnamese","Bars","Gluten-Free","Chinese","Barbeque","Italian","Desserts"],
    ["Chinese","Cafes","American (Traditional)","American (New)","Sandwiches","Breakfast & Brunch","Canadian (New)","Barbeque","Sushi Bars","Coffee & Tea","French","Caribbean","Middle Eastern","Mediterranean","Delis","Filipino","Fish & Chips","Burgers","Steakhouses","Lebanese"],
    ["Nightlife","Bars","American (Traditional)","American (New)","Pubs","Seafood","Sports Bars","Lounges","Desserts","Japanese","Cocktail Bars","Italian","Event Planning & Services","Burgers","Asian Fusion","Canadian (New)","Specialty Food","Fast Food","Caterers","Mexican"],
    ["Pizza","Italian","Sandwiches","Thai","Chinese","Bakeries","Event Planning & Services","Halal","Seafood","Caterers","Mediterranean","Indian","Specialty Food","Salad","Cafes","Asian Fusion","Greek","Nightlife","Vietnamese","French"],
    ["Nightlife","Bars","American (Traditional)","American (New)","Sandwiches","Breakfast & Brunch","Pizza","Event Planning & Services","Pubs","Sports Bars","Italian","Salad","Beer","Wine & Spirits","Caterers","Specialty Food","Cocktail Bars","Wine Bars","Seafood","Comfort Food"],
]
num_metacategories = len(metacategories)
d_metacategories = {}
for imc,mc in enumerate(metacategories):
    for c in mc:
        d_metacategories[c] = imc

mapping = {
    "Abruzzese": "abruzzese",
    "Acai Bowls": "acaibowls",
    "Afghan": "afghani",
    "African": "african",
    "Alentejo": "alentejo",
    "Algarve": "algarve",
    "Alsatian": "alsatian",
    "Altoatesine": "altoatesine",
    "American (New)": "newamerican",
    "American (Traditional)": "tradamerican",
    "Andalusian": "andalusian",
    "Apulian": "apulian",
    "Arab Pizza": "arabpizza",
    "Arabian": "arabian",
    "Argentine": "argentine",
    "Armenian": "armenian",
    "Arroceria / Paella": "arroceria_paella",
    "Asian Fusion": "asianfusion",
    "Asturian": "asturian",
    "Australian": "australian",
    "Austrian": "austrian",
    "Auvergnat": "auvergnat",
    "Azores": "azores",
    "Baden": "baden",
    "Bagels": "bagels",
    "Baguettes": "baguettes",
    "Bakeries": "bakeries",
    "Bangladeshi": "bangladeshi",
    "Barbeque": "bbq",
    "Basque": "basque",
    "Bavarian": "bavarian",
    "Beer Garden": "beergarden",
    "Beer Hall": "beerhall",
    "Beer, Wine & Spirits": "beer_and_wine",
    "Beer": "beer_and_wine",
    "Wine & Spirits": "beer_and_wine",
    "Wine Bars": "beer_and_wine",
    "Beira": "beira",
    "Beisl": "beisl",
    "Belgian": "belgian",
    "Berrichon": "berrichon",
    "Beverage Store": "beverage_stores",
    "Bistros": "bistros",
    "Black Sea": "blacksea",
    "Blowfish": "blowfish",
    "Bourguignon": "bourguignon",
    "Brasseries": "brasseries",
    "Brazilian Empanadas": "brazilianempanadas",
    "Brazilian": "brazilian",
    "Breakfast & Brunch": "breakfast_brunch",
    "Breweries": "breweries",
    "Brewpubs": "brewpubs",
    "British": "british",
    "Bubble Tea": "bubbletea",
    "Buffets": "buffets",
    "Bulgarian": "bulgarian",
    "Burgers": "burgers",
    "Burmese": "burmese",
    "Butcher": "butcher",
    "CSA": "csa",
    "Cafes": "cafes",
    "Cafeteria": "cafeteria",
    "Cajun/Creole": "cajun",
    "Calabrian": "calabrian",
    "Cambodian": "cambodian",
    "Canadian (New)": "newcanadian",
    "Candy Stores": "candy",
    "Canteen": "canteen",
    "Cantonese": "cantonese",
    "Caribbean": "caribbean",
    "Catalan": "catalan",
    "Central Brazilian": "centralbrazilian",
    "Chee Kufta": "cheekufta",
    "Cheese Shops": "cheese",
    "Cheesesteaks": "cheesesteaks",
    "Chicken Shop": "chickenshop",
    "Chicken Wings": "chicken_wings",
    "Chilean": "chilean",
    "Chimney Cakes": "chimneycakes",
    "Chinese": "chinese",
    "Chocolatiers & Shops": "chocolate",
    "Cideries": "cideries",
    "Coffee & Tea": "coffee",
    "Coffee Roasteries": "coffeeroasteries",
    "Colombian": "colombian",
    "Comfort Food": "comfortfood",
    "Congee": "congee",
    "Convenience Stores": "convenience",
    "Conveyor Belt Sushi": "conveyorsushi",
    "Corsican": "corsican",
    "Creperies": "creperies",
    "Cuban": "cuban",
    "Cucina campana": "cucinacampana",
    "Cupcakes": "cupcakes",
    "Curry Sausage": "currysausage",
    "Custom Cakes": "customcakes",
    "Cypriot": "cypriot",
    "Czech": "czech",
    "Czech/Slovakian": "czechslovakian",
    "Danish": "danish",
    "Delis": "delis",
    "Desserts": "desserts",
    "Dim Sum": "dimsum",
    "Diners": "diners",
    "Dinner Theater": "dinnertheater",
    "Distilleries": "distilleries",
    "Do-It-Yourself Food": "diyfood",
    "Dominican": "dominican",
    "Donburi": "donburi",
    "Donuts": "donuts",
    "Dumplings": "dumplings",
    "Eastern European": "eastern_european",
    "Eastern German": "easterngerman",
    "Eastern Mexican": "easternmexican",
    "Egyptian": "egyptian",
    "Emilian": "emilian",
    "Empanadas": "empanadas",
    "Eritrean": "eritrean",
    "Ethiopian": "ethiopian",
    "Fado Houses": "fado_houses",
    "Falafel": "falafel",
    "Farmers Market": "farmersmarket",
    "Fast Food": "hotdogs",
    "Filipino": "filipino",
    "Fischbroetchen": "fischbroetchen",
    "Fish & Chips": "fishnchips",
    "Flatbread": "flatbread",
    "Flemish": "flemish",
    "Fondue": "fondue",
    "Food Court": "food_court",
    "Food Delivery Services": "fooddeliveryservices",
    "Food Stands": "foodstands",
    "Food Trucks": "foodtrucks",
    "Franconian": "franconian",
    "Freiduria": "freiduria",
    "French Southwest": "sud_ouest",
    "French": "french",
    "Friulan": "friulan",
    "Fruits & Veggies": "markets",
    "Fuzhou": "fuzhou",
    "Galician": "galician",
    "Game Meat": "gamemeat",
    "Gastropubs": "gastropubs",
    "Gelato": "gelato",
    "Georgian": "georgian",
    "German": "german",
    "Giblets": "giblets",
    "Gluten-Free": "gluten_free",
    "Gozleme": "gozleme",
    "Greek": "greek",
    "Grocery": "grocery",
    "Guamanian": "guamanian",
    "Gyudon": "gyudon",
    "Hainan": "hainan",
    "Haitian": "haitian",
    "Hakka": "hakka",
    "Halal": "halal",
    "Hand Rolls": "handrolls",
    "Hawaiian": "hawaiian",
    "Health Markets": "healthmarkets",
    "Henghwa": "henghwa",
    "Herbs & Spices": "herbsandspices",
    "Hessian": "hessian",
    "Heuriger": "heuriger",
    "Himalayan/Nepalese": "himalayan",
    "Hokkien": "hokkien",
    "Homemade Food": "homemadefood",
    "Honduran": "honduran",
    "Honey": "honey",
    "Hong Kong Style Cafe": "hkcafe",
    "Horumon": "horumon",
    "Hot Dogs": "hotdog",
    "Hot Pot": "hotpot",
    "Hunan": "hunan",
    "Hungarian": "hungarian",
    "Iberian": "iberian",
    "Ice Cream & Frozen Yogurt": "icecream",
    "Imported Food": "importedfood",
    "Indian": "indpak",
    "Indonesian": "indonesian",
    "International Grocery": "intlgrocery",
    "International": "international",
    "Internet Cafes": "internetcafe",
    "Irish": "irish",
    "Island Pub": "island_pub",
    "Israeli": "israeli",
    "Italian": "italian",
    "Izakaya": "izakaya",
    "Jaliscan": "jaliscan",
    "Japanese Curry": "japacurry",
    "Japanese": "japanese",
    "Jewish": "jewish",
    "Juice Bars & Smoothies": "juicebars",
    "Kaiseki": "kaiseki",
    "Kebab": "kebab",
    "Kombucha": "kombucha",
    "Kopitiam": "kopitiam",
    "Korean": "korean",
    "Kosher": "kosher",
    "Kurdish": "kurdish",
    "Kushikatsu": "kushikatsu",
    "Lahmacun": "lahmacun",
    "Laos": "laos",
    "Laotian": "laotian",
    "Latin American": "latin",
    "Lebanese": "lebanese",
    "Ligurian": "ligurian",
    "Live/Raw Food": "raw_food",
    "Lumbard": "lumbard",
    "Lyonnais": "lyonnais",
    "Macarons": "macarons",
    "Madeira": "madeira",
    "Malaysian": "malaysian",
    "Mamak": "mamak",
    "Mauritius": "mauritius",
    "Meaderies": "meaderies",
    "Meat Shops": "meats",
    "Meatballs": "meatballs",
    "Mediterranean": "mediterranean",
    "Mexican": "mexican",
    "Middle Eastern": "mideastern",
    "Milk Bars": "milkbars",
    "Minho": "minho",
    "Modern Australian": "modern_australian",
    "Modern European": "modern_european",
    "Mongolian": "mongolian",
    "Moroccan": "moroccan",
    "Napoletana": "napoletana",
    "New Mexican Cuisine": "newmexican",
    "New Zealand": "newzealand",
    "Nicaraguan": "nicaraguan",
    "Nicoise": "nicois",
    "Night Food": "nightfood",
    "Nikkei": "nikkei",
    "Noodles": "noodles",
    "Norcinerie": "norcinerie",
    "Northeastern Brazilian": "northeasternbrazilian",
    "Northern Brazilian": "northernbrazilian",
    "Northern German": "northerngerman",
    "Northern Mexican": "northernmexican",
    "Nyonya": "nyonya",
    "Oaxacan": "oaxacan",
    "Oden": "oden",
    "Okinawan": "okinawan",
    "Okonomiyaki": "okonomiyaki",
    "Olive Oil": "oliveoil",
    "Onigiri": "onigiri",
    "Open Sandwiches": "opensandwiches",
    "Organic Stores": "organic_stores",
    "Oriental": "oriental",
    "Ottoman Cuisine": "ottomancuisine",
    "Oyakodon": "oyakodon",
    "PF/Comercial": "pfcomercial",
    "Pakistani": "pakistani",
    "Palatine": "palatine",
    "Pan Asian": "panasian",
    "Pancakes": "pancakes",
    "Parent Cafes": "eltern_cafes",
    "Parma": "parma",
    "Pasta Shops": "pastashops",
    "Patisserie/Cake Shop": "cakeshop",
    "Pekinese": "pekinese",
    "Persian/Iranian": "persian",
    "Peruvian": "peruvian",
    "Piadina": "piadina",
    "Piemonte": "piemonte",
    "Pierogis": "pierogis",
    "Pita": "pita",
    "Pizza": "pizza",
    "Poke": "poke",
    "Polish": "polish",
    "Polynesian": "polynesian",
    "Pop-Up Restaurants": "popuprestaurants",
    "Popcorn Shops": "popcorn",
    "Portuguese": "portuguese",
    "Potatoes": "potatoes",
    "Poutineries": "poutineries",
    "Pretzels": "pretzels",
    "Provencal": "provencal",
    "Pub Food": "pubfood",
    "Pueblan": "pueblan",
    "Puerto Rican": "puertorican",
    "Ramen": "ramen",
    "Reunion": "reunion",
    "Rhinelandian": "rhinelandian",
    "Ribatejo": "ribatejo",
    "Rice": "riceshop",
    "Robatayaki": "robatayaki",
    "Rodizios": "rodizios",
    "Roman": "roman",
    "Romanian": "romanian",
    "Rotisserie Chicken": "rotisserie_chicken",
    "Russian": "russian",
    "Salad": "salad",
    "Salvadoran": "salvadoran",
    "Sandwiches": "sandwiches",
    "Sardinian": "sardinian",
    "Scandinavian": "scandinavian",
    "Schnitzel": "schnitzel",
    "Scottish": "scottish",
    "Seafood Markets": "seafoodmarkets",
    "Seafood": "seafood",
    "Senegalese": "senegalese",
    "Serbo Croatian": "serbocroatian",
    "Shanghainese": "shanghainese",
    "Shaved Ice": "shavedice",
    "Shaved Snow": "shavedsnow",
    "Sicilian": "sicilian",
    "Signature Cuisine": "signature_cuisine",
    "Singaporean": "singaporean",
    "Slovakian": "slovakian",
    "Smokehouse": "smokehouse",
    "Soba": "soba",
    "Somali": "somali",
    "Soul Food": "soulfood",
    "Soup": "soup",
    "South African": "southafrican",
    "Southern": "southern",
    "Spanish": "spanish",
    "Specialty Food": "gourmet",
    "Sri Lankan": "srilankan",
    "Steakhouses": "steak",
    "Street Vendors": "streetvendors",
    "Sukiyaki": "sukiyaki",
    "Supper Clubs": "supperclubs",
    "Sushi Bars": "sushi",
    "Swabian": "swabian",
    "Swedish": "swedish",
    "Swiss Food": "swissfood",
    "Syrian": "syrian",
    "Szechuan": "szechuan",
    "Tabernas": "tabernas",
    "Tacos": "tacos",
    "Taiwanese": "taiwanese",
    "Takoyaki": "takoyaki",
    "Tamales": "tamales",
    "Tapas Bars": "tapas",
    "Tapas/Small Plates": "tapasmallplates",
    "Tavola Calda": "tavolacalda",
    "Tea Rooms": "tea",
    "Tempura": "tempura",
    "Teochew": "teochew",
    "Teppanyaki": "teppanyaki",
    "Tex-Mex": "tex-mex",
    "Thai": "thai",
    "Themed Cafes": "themedcafes",
    "Tonkatsu": "tonkatsu",
    "Traditional Norwegian": "norwegian",
    "Traditional Swedish": "traditional_swedish",
    "Tras-os-Montes": "tras_os_montes",
    "Trattorie": "trattorie",
    "Trinidadian": "trinidadian",
    "Turkish Ravioli": "turkishravioli",
    "Turkish": "turkish",
    "Tuscan": "tuscan",
    "Udon": "udon",
    "Ukrainian": "ukrainian",
    "Unagi": "unagi",
    "Uzbek": "uzbek",
    "Vegan": "vegan",
    "Vegetarian": "vegetarian",
    "Venetian": "venetian",
    "Venezuelan": "venezuelan",
    "Venison": "venison",
    "Vietnamese": "vietnamese",
    "Waffles": "waffles",
    "Water Stores": "waterstores",
    "Western Style Japanese Food": "westernjapanese",
    "Wine Tasting Room": "winetastingroom",
    "Wineries": "wineries",
    "Wok": "wok",
    "Wraps": "wraps",
    "Yakiniku": "yakiniku",
    "Yakitori": "yakitori",
    "Yucatan": "yucatan",
    "Yugoslav": "yugoslav",
}

def get_combined_df(fname_reviews, fname_businesses):
    """
    Takes filenames for review and business kaggle dataset JSONs and returns
    a pandas dataframe of their combined information
    Reviews: https://www.kaggle.com/yelp-dataset/yelp-dataset#yelp_academic_dataset_review.json
    Businesses: https://www.kaggle.com/yelp-dataset/yelp-dataset#yelp_academic_dataset_business.json
    """
    df_reviews = pd.read_json(fname_reviews,lines=True).drop(columns=["review_id","user_id","funny","cool","useful"])
    df_businesses = pd.read_json(fname_businesses,lines=True).drop(columns=["address","city","latitude","longitude","neighborhood","postal_code","state","hours","is_open"])
    df = df_reviews.merge(df_businesses, on=["business_id"], how="left")
    df = df.drop(columns=["attributes"])
    df = df[(df.review_count>150) & (df.stars_y > 2.5) & (df.stars_x > 2.5)]
    df = df[df.categories.str.contains("Restaurants", na=False)]
    df.reset_index(inplace=True)
    return df

if __name__ == "__main__":

    df = get_combined_df(
            "yelp_academic_dataset_reviews.json",
            "yelp_academic_dataset_business.json",
            )

    # Make k-hot encoded vectors for metacategories
    all_vecs = []
    for categs in tqdm(df.categories.str.split(",").values):
        v = [0 for _ in range(num_metacategories)]
        for c in categs:
            code = d_metacategories.get(c.strip(),-1)
            if code >= 0: v[code] = 1
        all_vecs.append(v)
    all_vecs = np.array(all_vecs)

    # Make them separate columns in the dataframe
    for i in range(num_metacategories):
        df["cat_{}".format(i)] = all_vecs[:,i]

    stop_words = set(stopwords.words('english'))
    stop_words.update(set(["'m", "n't", "'ve", "'re", "'s"]))
    new_texts = []

    for text in tqdm(df["text"]):
        filtered_text = clean_data(text)
        # print(filtered_text)
        # word_tokens = word_tokenize(text.lower())
        # filtered_text = " ".join([w for w in word_tokens if not w in stop_words])
        new_texts.append(" ".join(filtered_text))
    new_texts = np.array(new_texts)
    df["text"] = np.array(new_texts)

    # # Unpack column by column into an num_review-by-num_metacategories matrix again
    # target_vecs = np.vstack([
    #     df["cat_{}".format(i)] for i in range(num_metacategories)
    #     ]).T
    # print target_vecs

    df.to_pickle("combined_data.pkl")
