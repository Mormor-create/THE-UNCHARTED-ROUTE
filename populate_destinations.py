
from app import create_app
from extensions import db
from app.models.destination import Destination


# Every non-image field is populated.
# Coordinates represent the main destination or its principal visitor hub.

DESTINATIONS = [
    {
        "name": "Mauritius",
        "slug": "mauritius",
        "country": "Mauritius",
        "county": None,
        "region": "Indian Ocean",
        "short_description": (
            "A tropical island destination known for turquoise lagoons, "
            "white-sand beaches, volcanic landscapes and rich Creole culture."
        ),
        "description": """
Mauritius is an Indian Ocean island destination celebrated for its beautiful
coastline, warm turquoise waters, coral reefs and diverse cultural heritage.

Visitors can enjoy beach escapes, boat excursions, snorkelling, diving,
waterfalls, mountain scenery, nature experiences and local food. The island
also offers opportunities to discover its Creole, Indian, African, Chinese
and European cultural influences.

From the beaches and lagoons of the coast to the green interior and
picturesque viewpoints, Mauritius offers a blend of relaxation, nature,
adventure and luxury travel.

The coordinates identify Port Louis, the island's capital and principal
urban gateway.
""".strip(),
        "latitude": -20.1609,
        "longitude": 57.5012,
        "meta_title": "Mauritius Holidays & Island Experiences | The Uncharted Route",
        "meta_description": (
            "Discover Mauritius with The Uncharted Route. Explore tropical "
            "beaches, turquoise lagoons, island adventures, culture and "
            "beautiful nature escapes."
        ),
    },
    {
        "name": "Madagascar",
        "slug": "madagascar",
        "country": "Madagascar",
        "county": None,
        "region": "Indian Ocean",
        "short_description": (
            "An extraordinary island destination known for unique wildlife, "
            "lemurs, baobab landscapes, rainforests and distinctive culture."
        ),
        "description": """
Madagascar is one of the world's most distinctive island destinations,
renowned for its extraordinary biodiversity, dramatic landscapes and
cultural heritage.

The island is home to lemurs, chameleons, baobab trees and many plant and
animal species found nowhere else in the wild. Its landscapes range from
rainforests and highland scenery to dry forests, limestone formations and
beautiful coastal environments.

Travellers can discover nature reserves, wildlife experiences, traditional
communities, local markets and coastal escapes. Madagascar is particularly
suited to travellers interested in conservation, photography, nature and
adventure.

The coordinates identify Antananarivo, the country's capital and principal
urban gateway.
""".strip(),
        "latitude": -18.8792,
        "longitude": 47.5079,
        "meta_title": "Madagascar Wildlife & Nature Experiences | The Uncharted Route",
        "meta_description": (
            "Explore Madagascar with The Uncharted Route. Discover lemurs, "
            "baobab landscapes, rainforests, wildlife, culture and island "
            "adventures."
        ),
    },
    {
        "name": "Egypt",
        "slug": "egypt",
        "country": "Egypt",
        "county": None,
        "region": "North Africa",
        "short_description": (
            "A historic destination of ancient monuments, Nile landscapes, "
            "desert adventures, vibrant cities and Red Sea escapes."
        ),
        "description": """
Egypt offers an extraordinary journey through ancient history, living
culture and varied natural landscapes.

From the pyramids and monuments of the ancient Egyptian civilisation to
the temples along the Nile, the country holds some of the world's most
recognisable archaeological and cultural landmarks.

Visitors can explore historic Cairo, discover museums and traditional
markets, experience Nile cruises, venture into desert landscapes and enjoy
the Red Sea's coastal environments. Egypt combines heritage, architecture,
food, adventure and relaxation in one destination.

The coordinates identify Cairo, the country's capital and a major starting
point for cultural and historical journeys.
""".strip(),
        "latitude": 30.0444,
        "longitude": 31.2357,
        "meta_title": "Egypt Holidays & Historical Experiences | The Uncharted Route",
        "meta_description": (
            "Discover Egypt with The Uncharted Route. Explore ancient "
            "monuments, the Nile, historic cities, desert landscapes and "
            "Red Sea experiences."
        ),
    },
    {
        "name": "Elementaita",
        "slug": "elementaita",
        "country": "Kenya",
        "county": "Nakuru",
        "region": "Rift Valley",
        "short_description": (
            "A scenic Rift Valley escape featuring Lake Elementaita, "
            "birdlife, open landscapes and peaceful nature experiences."
        ),
        "description": """
Elementaita is a scenic destination in Kenya's Great Rift Valley, centred
around Lake Elementaita, a shallow alkaline lake recognised for its
ecological importance and birdlife.

The surrounding landscape offers open plains, escarpment views, natural
habitats and opportunities for birdwatching, photography and quiet
countryside escapes. The lake is part of the Kenya Lake System in the
Great Rift Valley UNESCO World Heritage property.

Visitors can enjoy nature-focused stays, scenic drives, birdwatching and
exploration of the surrounding Rift Valley landscape.

The coordinates identify the Lake Elementaita area in Nakuru County.
""".strip(),
        "latitude": -0.4597,
        "longitude": 36.2594,
        "meta_title": "Lake Elementaita Nature Escapes | The Uncharted Route",
        "meta_description": (
            "Explore Elementaita in Kenya's Great Rift Valley. Discover "
            "Lake Elementaita, birdwatching, scenic landscapes and "
            "peaceful nature experiences."
        ),
    },
    {
        "name": "Beijing",
        "slug": "beijing",
        "country": "China",
        "county": None,
        "region": "Beijing Municipality",
        "short_description": (
            "China's historic capital, known for imperial landmarks, "
            "traditional neighbourhoods, cultural heritage and the Great Wall."
        ),
        "description": """
Beijing is China's capital and one of its most important historical and
cultural destinations. The city brings together imperial architecture,
traditional neighbourhoods, contemporary urban life and renowned cuisine.

Visitors can explore the Forbidden City, Tiananmen area, the Temple of
Heaven, traditional hutong neighbourhoods and sections of the Great Wall
accessible from the Beijing region.

Beijing offers opportunities to discover Chinese history, architecture,
local food, art and modern city culture. It is an excellent starting point
for travellers interested in China's imperial heritage and contemporary
identity.

The coordinates identify central Beijing.
""".strip(),
        "latitude": 39.9042,
        "longitude": 116.4074,
        "meta_title": "Beijing Travel & Cultural Experiences | The Uncharted Route",
        "meta_description": (
            "Discover Beijing with The Uncharted Route. Explore imperial "
            "landmarks, the Forbidden City, traditional hutongs, Chinese "
            "culture and the Great Wall region."
        ),
    },
    {
        "name": "Shanghai",
        "slug": "shanghai",
        "country": "China",
        "county": None,
        "region": "Shanghai Municipality",
        "short_description": (
            "A dynamic Chinese metropolis known for its skyline, waterfront, "
            "historic architecture, shopping and contemporary culture."
        ),
        "description": """
Shanghai is a major international city where historic neighbourhoods,
modern architecture, waterfront scenery and contemporary Chinese culture
meet.

The city is known for the Bund, its impressive skyline across the Huangpu
River, historic streets, traditional gardens, museums, galleries and
diverse food culture. Its neighbourhoods offer a mix of heritage buildings,
creative spaces, shopping districts and modern urban attractions.

Visitors can experience riverfront views, explore local markets, discover
Chinese and international cuisine, and enjoy the city's art, design and
nightlife scenes.

The coordinates identify central Shanghai.
""".strip(),
        "latitude": 31.2304,
        "longitude": 121.4737,
        "meta_title": "Shanghai City Experiences & Travel | The Uncharted Route",
        "meta_description": (
            "Explore Shanghai with The Uncharted Route. Discover the Bund, "
            "city skyline, historic neighbourhoods, gardens, food and "
            "contemporary Chinese culture."
        ),
    },
    {
        "name": "Hong Kong",
        "slug": "hong-kong",
        "country": "China",
        "county": None,
        "region": "Hong Kong Special Administrative Region",
        "short_description": (
            "A vibrant harbour city combining dramatic skylines, island "
            "landscapes, traditional markets, food and cultural experiences."
        ),
        "description": """
Hong Kong is a dynamic destination known for its dramatic harbour,
recognisable skyline, lively neighbourhoods and distinctive blend of
Chinese and international influences.

Visitors can explore Victoria Harbour, traditional markets, historic
districts, temples, museums, waterfront promenades and the city's celebrated
food scene. Beyond the central urban areas, Hong Kong also offers islands,
hiking trails, beaches and scenic countryside.

The destination combines energetic city exploration with opportunities
for nature, culture, shopping, dining and coastal experiences.

The coordinates identify the Central and harbourfront area of Hong Kong
Island.
""".strip(),
        "latitude": 22.2819,
        "longitude": 114.1582,
        "meta_title": "Hong Kong Travel & City Experiences | The Uncharted Route",
        "meta_description": (
            "Discover Hong Kong with The Uncharted Route. Explore Victoria "
            "Harbour, city skylines, markets, islands, hiking trails and "
            "local food experiences."
        ),
    },
    {
        "name": "Xi'an",
        "slug": "xian",
        "country": "China",
        "county": None,
        "region": "Shaanxi Province",
        "short_description": (
            "An ancient Chinese capital famous for the Terracotta Army, "
            "historic city walls, cultural heritage and local cuisine."
        ),
        "description": """
Xi'an is one of China's most historically significant cities and a major
destination for travellers interested in ancient Chinese civilisation.

The city is best known for the Terracotta Army, an extraordinary
archaeological discovery associated with China's first emperor. Other
highlights include the Ancient City Wall, the Bell and Drum Towers, the
Muslim Quarter and historic cultural sites.

Xi'an also offers a distinctive food culture, traditional markets and
opportunities to explore the history of the Silk Road and the development
of imperial China.

The coordinates identify central Xi'an.
""".strip(),
        "latitude": 34.3416,
        "longitude": 108.9398,
        "meta_title": "Xi'an Historical & Cultural Experiences | The Uncharted Route",
        "meta_description": (
            "Explore Xi'an with The Uncharted Route. Discover the "
            "Terracotta Army, ancient city walls, Silk Road history, "
            "heritage sites and local cuisine."
        ),
    },
    {
        "name": "Chongqing",
        "slug": "chongqing",
        "country": "China",
        "county": None,
        "region": "Chongqing Municipality",
        "short_description": (
            "A dramatic mountain city known for its layered skyline, "
            "Yangtze River scenery, hotpot cuisine and night views."
        ),
        "description": """
Chongqing is a large southwestern Chinese municipality set among hills
and river valleys, where the Yangtze and Jialing rivers meet.

The city's distinctive terrain creates a dramatic urban landscape of
elevated roads, bridges, hillside neighbourhoods and striking night views.
Visitors can explore historic streets, riverfront districts, traditional
architecture, local markets and the city's famous hotpot food culture.

Chongqing is also a gateway to wider regional exploration, including
river journeys and landscapes in the surrounding municipality.

The coordinates identify central Chongqing.
""".strip(),
        "latitude": 29.5630,
        "longitude": 106.5516,
        "meta_title": "Chongqing City & Cultural Experiences | The Uncharted Route",
        "meta_description": (
            "Discover Chongqing with The Uncharted Route. Explore its "
            "mountain cityscape, river views, historic streets, night "
            "scenery and famous hotpot cuisine."
        ),
    },
    {
        "name": "Chengdu",
        "slug": "chengdu",
        "country": "China",
        "county": None,
        "region": "Sichuan Province",
        "short_description": (
            "The capital of Sichuan, known for giant pandas, relaxed "
            "teahouse culture, spicy cuisine and rich regional heritage."
        ),
        "description": """
Chengdu is the capital of Sichuan Province and a major destination for
culture, food and wildlife experiences in southwestern China.

The city is widely associated with giant panda conservation and research.
Visitors can discover panda-related experiences, traditional teahouses,
historic streets, temples, parks and local markets.

Chengdu is also celebrated for Sichuan cuisine, known for its bold flavours
and distinctive use of Sichuan pepper. The city offers a relaxed urban
atmosphere while providing access to wider cultural and natural attractions
across Sichuan Province.

The coordinates identify central Chengdu.
""".strip(),
        "latitude": 30.5728,
        "longitude": 104.0668,
        "meta_title": "Chengdu Panda & Cultural Experiences | The Uncharted Route",
        "meta_description": (
            "Explore Chengdu with The Uncharted Route. Discover giant panda "
            "experiences, Sichuan cuisine, traditional teahouses, temples "
            "and regional culture."
        ),
    },
]


def normalize(value):
    return (value or "").strip().casefold()


app = create_app()

with app.app_context():

    print("\n" + "=" * 100)
    print("THE UNCHARTED ROUTE — COMPLETE DESTINATION POPULATION")
    print("=" * 100)

    existing_destinations = Destination.query.all()

    added = []
    updated = []
    unchanged = []

    try:
        for data in DESTINATIONS:

            name_key = normalize(data["name"])
            slug_key = normalize(data["slug"])

            # Match an existing destination by either name or slug.
            matches = [
                destination
                for destination in existing_destinations
                if (
                    normalize(destination.name) == name_key
                    or normalize(destination.slug) == slug_key
                )
            ]

            # Never silently choose between conflicting records.
            if len(matches) > 1:
                raise ValueError(
                    f"Multiple existing records match {data['name']}. "
                    "Resolve the duplicates before continuing."
                )

            destination = matches[0] if matches else None

            # Protect other records from name/slug collisions.
            for other in existing_destinations:
                if other is destination:
                    continue

                if (
                    normalize(other.name) == name_key
                    or normalize(other.slug) == slug_key
                ):
                    raise ValueError(
                        f"Name or slug collision for {data['name']} "
                        f"with existing destination {other.name}."
                    )

            if destination is None:
                destination = Destination()
                db.session.add(destination)
                existing_destinations.append(destination)
                added.append(data["name"])
                action = "ADDED"
            else:
                updated.append(data["name"])
                action = "COMPLETED / UPDATED"

            # Populate every non-image field.
            destination.name = data["name"]
            destination.slug = data["slug"]
            destination.country = data["country"]
            destination.county = data["county"]
            destination.region = data["region"]
            destination.short_description = data["short_description"]
            destination.description = data["description"]
            destination.latitude = data["latitude"]
            destination.longitude = data["longitude"]
            destination.meta_title = data["meta_title"]
            destination.meta_description = data["meta_description"]

            destination.active = True
            destination.featured = False
            destination.show_on_homepage = False

            # Intentionally do not assign:
            # destination.featured_image_id
            # destination.banner_image_id
            #
            # This preserves existing image assignments on updates.

            print(f"{action}: {data['name']}")

        db.session.commit()

    except Exception as error:
        db.session.rollback()

        print("\n" + "=" * 100)
        print("POPULATION FAILED — ALL CHANGES ROLLED BACK")
        print("=" * 100)
        print(error)

        raise

    # Verify persisted records after commit.
    print("\n" + "=" * 100)
    print("DESTINATION VERIFICATION")
    print("=" * 100)

    for data in DESTINATIONS:
        destination = Destination.query.filter_by(
            slug=data["slug"]
        ).first()

        if not destination:
            print(f"MISSING: {data['name']}")
            continue

        print(
            f"{destination.name:<20} | "
            f"{destination.country:<25} | "
            f"{'ACTIVE' if destination.active else 'INACTIVE'} | "
            f"Coordinates: {destination.latitude}, {destination.longitude} | "
            f"Description: {'YES' if destination.description else 'NO'} | "
            f"SEO: {'YES' if destination.meta_title and destination.meta_description else 'NO'}"
        )

    # Final complete catalogue.
    print("\n" + "=" * 100)
    print("FINAL DESTINATION CATALOGUE")
    print("=" * 100)

    all_destinations = Destination.query.order_by(
        Destination.name.asc()
    ).all()

    for destination in all_destinations:
        status = "ACTIVE" if destination.active else "INACTIVE"
        print(f"{destination.name:<40} | {destination.country:<25} | {status}")

    active_count = sum(1 for d in all_destinations if d.active)
    inactive_count = len(all_destinations) - active_count

    print("\n" + "=" * 100)
    print("FINAL SUMMARY")
    print("=" * 100)

    print(f"New records added: {len(added)}")
    print(f"Existing records completed/updated: {len(updated)}")
    print(f"Total destinations: {len(all_destinations)}")
    print(f"Active destinations: {active_count}")
    print(f"Inactive destinations: {inactive_count}")

    print("\nIMAGE STATUS")
    print("Image fields were intentionally left untouched.")

    print("\nDestination population completed successfully.")
