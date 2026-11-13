"""
===============================================================================
THE UNCHARTED ROUTE — BLOG CATALOGUE POPULATION
===============================================================================
Purpose
-------
Populate the initial The Uncharted Route launch Blog catalogue.
IMPORTANT
---------
The Blog catalogue already contains one published launch article:
    The Wild at Your Doorstep: Discovering the Magic of Nairobi National Park
That article is PRESERVED and will not be updated, duplicated, deleted, or
otherwise modified by this script.

The final launch catalogue should contain exactly four posts:

    1. Existing:
       The Wild at Your Doorstep: Discovering the Magic of Nairobi National Park

    2. New:
       Destinations & Getaways article

    3. New:
       Culture & Local Experiences article

    4. New:
       Stays & Slow Travel article

The script creates ONLY the three missing articles.

The existing four BlogCategory records are reused:

    - Safari & Wildlife
    - Destinations & Getaways
    - Culture & Local Experiences
    - Stays & Slow Travel

Editorial format
----------------
The existing published article was audited before this script was created.

Its content uses HTML/Rich Text with:

    - <h1>
    - <h2>
    - <h3>
    - <p>
    - <strong>
    - <em>
    - <ul>
    - <li>
    - <blockquote>
    - <hr>

The three new articles intentionally follow the same editorial language and
HTML structure without duplicating the existing article.

Safety
------
Default execution is READ-ONLY / DRY-RUN.

No database mutation occurs unless:

    --apply

is explicitly supplied.

When --apply is supplied:

    - all changes occur inside one transaction
    - any error triggers rollback
    - no existing BlogPost is modified
    - no existing BlogCategory is modified
    - no media records are created
    - no views are fabricated
    - no likes are fabricated
    - no shares are fabricated
    - no newsletter activity is fabricated
    - no comments are created
    - no bookings/inquiries are created

Duplicate protection
---------------------
A post is considered already present when its slug exists.
The script also protects against duplicate titles.
If a planned post already exists, it is REUSED and is not modified.

Run
---
Dry run:

    python scripts/populate_blog_catalogue.py

Apply:

    python scripts/populate_blog_catalogue.py --apply
===============================================================================
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------------------
# PROJECT BOOTSTRAP
# --------------------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("FLASK_ENV", "development")

from flask import Flask
from extensions import db
from app.models.blog_post import BlogPost
from app.models.blog_category import BlogCategory

# =============================================================================
# APPLICATION
# =============================================================================
def create_population_app():
    from app import create_app

    return create_app()

# =============================================================================
# CONSTANTS
# =============================================================================
SEPARATOR = "=" * 88
SUB_SEPARATOR = "-" * 88
EXPECTED_FINAL_POST_COUNT = 4
NEW_POST_COUNT = 3
AUTHOR_NAME = "The Uncharted Route"
AUTHOR_TITLE = "Travel & Experience Editorial Team"
STATUS_PUBLISHED = "Published"

# =============================================================================
# HTML / TEXT HELPERS
# =============================================================================
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")

def strip_html(content: str) -> str:
    """Return readable plain text from stored HTML content."""

    if not content:
        return ""

    text = HTML_TAG_PATTERN.sub(" ", content)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculate_word_count(content: str) -> int:
    """Calculate article word count from HTML content."""

    plain_text = strip_html(content)

    if not plain_text:
        return 0

    return len(plain_text.split())


def calculate_reading_time(content: str, words_per_minute: int = 200) -> int:
    """Calculate rounded-up reading time."""

    word_count = calculate_word_count(content)

    if word_count <= 0:
        return 1

    return max(
        1,
        (word_count + words_per_minute - 1) // words_per_minute,
    )


# =============================================================================
# BLOG CONTENT
# =============================================================================
DESTINATIONS_CONTENT = """
<h1>Kenya Beyond the Obvious: Places Worth Taking Your Time To Discover</h1>

<p>Kenya is often introduced through its famous wildlife, but the country is much
more than a collection of safari destinations. Beyond the places that appear
most often in travel brochures are coastal towns, mountain landscapes, forested
retreats, creative neighbourhoods and quiet corners where the journey itself
becomes part of the experience.</p>

<p><strong>The most memorable Kenyan journeys are not always the ones that cover
the greatest distance. Sometimes they are the journeys that leave enough room
to notice where you are.</strong></p>

<h2>There Is More to Kenya Than a Single Itinerary</h2>

<p>For a first-time visitor, it can be tempting to build a trip around a list of
the country's most recognisable names. A safari, a few days at the coast and a
return to Nairobi can make for an excellent introduction, but Kenya rewards
travellers who allow themselves to look beyond the obvious.</p>

<p>Different parts of the country offer remarkably different rhythms. The
landscape changes from open savannah and highland country to forests, lakes,
farmland and the Indian Ocean coast. Communities, food traditions, architecture
and everyday life change with them.</p>

<p>That variety makes it possible to shape a journey around interests rather than
simply collecting destinations.</p>

<h2>Start With the Kind of Journey You Want</h2>

<p>Before deciding where to go, think about what you want the journey to feel
like. Do you want a peaceful retreat, an active adventure, a cultural
experience, time in nature or a combination of several?</p>

<p>A traveller looking for stillness might prefer a slower stay surrounded by
nature. Someone interested in food and creativity may enjoy spending more time
in Nairobi and exploring its independent spaces. A coastal journey can be built
around the sea while still leaving room for heritage, local food and
neighbourhood discoveries.</p>

<p>There is no single correct way to experience Kenya. The strongest itinerary
is often the one that reflects your curiosity rather than someone else's
checklist.</p>

<h2>Coast, Culture and the Rhythm of the Indian Ocean</h2>

<p>Kenya's coast offers more than beaches. The Indian Ocean shapes the food,
architecture, history and daily rhythm of the region, creating an experience
that feels distinctly different from inland Kenya.</p>

<p>Places such as Diani and Watamu offer opportunities to slow down beside the
ocean, while historic coastal communities provide another way to understand
the region through architecture, cuisine and cultural heritage.</p>

<p>Take time to notice the details. Explore local food, learn about the history
of the places you visit, and allow a beach stay to become more than a sequence
of hours beside the water.</p>

<h3>Make Space for the Coast Beyond the Resort</h3>

<p>A beautiful hotel can be part of a coastal journey, but it does not have to
be the entire experience. Spend time discovering local surroundings, support
responsible businesses and approach cultural sites with respect.</p>

<p>The coast becomes more memorable when the landscape, people, history and food
are part of the story.</p>

<h2>Highlands, Forests and Mountain Landscapes</h2>

<p>Kenya's highlands offer a different kind of escape. Cooler temperatures,
green landscapes, farms and mountain views create ideal conditions for travellers
who want to slow down without giving up the sense of discovery.</p>

<p>Mount Kenya and the surrounding highland areas provide opportunities for
nature, outdoor activities, scenic drives and restorative stays. The experience
does not have to involve a demanding expedition. Sometimes simply spending a
few days in a beautiful landscape is enough.</p>

<p>These destinations also remind us that travel can be about atmosphere as much
as activity. A morning walk, a long lunch, a view across the hills or an evening
beside a fire can become the moments you remember most.</p>

<h2>Choose Fewer Places and Experience Them Better</h2>

<p>One of the easiest ways to make a journey feel rushed is to change locations
every day. Moving constantly may create an impressive itinerary on paper, but
it can leave little time to understand any of the places you visit.</p>

<p>Consider staying longer in fewer destinations. This gives you time to settle
in, discover local recommendations, return to a favourite place and notice how
the atmosphere changes throughout the day.</p>

<ul>
    <li>Choose destinations that genuinely interest you.</li>
    <li>Allow realistic travel time between locations.</li>
    <li>Leave unplanned space in the itinerary.</li>
    <li>Support locally owned businesses where possible.</li>
    <li>Give yourself time to experience a place rather than simply photograph it.</li>
</ul>

<p>Slower travel does not mean doing nothing. It means giving experiences enough
space to become meaningful.</p>

<h2>Let the Journey Connect the Destinations</h2>

<p>Some of Kenya's most interesting moments happen between major stops. A scenic
road, a conversation over coffee, a roadside market, a farm visit or an
unexpected viewpoint can become part of the story.</p>

<p>Instead of treating travel time as something to endure, consider how the route
itself can contribute to the experience. A thoughtful itinerary can turn
movement between destinations into another opportunity for discovery.</p>

<h3>Travel With Curiosity</h3>

<p>Ask questions. Try something unfamiliar. Learn a few local words. Taste food
you have never ordered before. Notice the landscapes changing outside the
window.</p>

<p>Curiosity transforms a journey from transportation between points into an
experience in its own right.</p>

<h2>Responsible Travel Makes the Experience Better</h2>

<p>Beautiful destinations depend on healthy environments, thriving communities
and people who care for the places they call home.</p>

<p>Responsible travel is therefore not an additional layer added after the
itinerary is complete. It can be part of the experience from the beginning.</p>

<p>Respect local customs, protect natural spaces, minimise unnecessary waste,
follow conservation guidance and choose businesses that value the destinations
they operate in.</p>

<blockquote>
    <p>The places we remember most clearly are often the ones we gave ourselves
    enough time to truly notice.</p>
</blockquote>

<h2>Explore. Experience. Remember.</h2>

<p>Kenya does not need to be experienced as a race from one famous attraction to
the next. Its landscapes, communities, food, wildlife and places to stay invite
a different approach: one that leaves room for curiosity and connection.</p>

<p>At The Uncharted Route, we believe the best journeys are shaped around the
traveller, the destination and the moments that happen between the planned
ones.</p>

<p><strong>Choose a place that interests you. Give it time. Let the journey
unfold.</strong></p>

<hr>

<p><em>Travel thoughtfully. Stay curious. Leave room for discovery.</em></p>
"""


CULTURE_CONTENT = """
<h1>Beyond the Guidebook: Discovering Kenya Through Local Experiences</h1>

<p>A destination is more than its landscapes and attractions. It is also the
food shared around a table, the stories attached to a place, the craft passed
between generations and the ordinary rhythms of daily life.</p>

<p><strong>Some of the most meaningful travel experiences happen when you stop
looking at a destination from the outside and become curious about how people
experience it every day.</strong></p>

<h2>Culture Is Not a Performance</h2>

<p>Travel often introduces visitors to carefully presented versions of culture.
These experiences can be valuable, particularly when they are created and led
by local communities, but cultural discovery can also happen in much quieter
ways.</p>

<p>A conversation with a maker, a visit to a local food producer, an afternoon
spent learning about a craft or a meal shared in a neighbourhood can reveal
something a conventional sightseeing stop cannot.</p>

<p>The key is approach. Culture deserves curiosity and respect rather than the
expectation that every encounter should become a photograph or performance.</p>

<h2>Start With Food</h2>

<p>Food is one of the simplest ways to begin understanding a place. Kenya's
culinary traditions reflect geography, history, community and everyday life.</p>

<p>From familiar dishes to regional specialities, food can tell stories about
where ingredients come from, how families cook and how traditions change over
time.</p>

<p>Try local dishes with an open mind. Ask about ingredients. Learn where a meal
comes from. When possible, support independent restaurants, producers and food
businesses that are rooted in their communities.</p>

<h3>Let a Meal Become an Experience</h3>

<p>A meal does not need to be elaborate to be memorable. Sometimes the setting,
the conversation and the story behind the food matter more than presentation.</p>

<p>Slow down enough to ask questions and appreciate what is on the table. Food
becomes much more interesting when it is treated as part of a culture rather
than simply something to consume.</p>

<h2>Meet the People Behind the Craft</h2>

<p>Kenya has a rich creative landscape shaped by artists, designers, artisans,
photographers, makers and independent creative communities.</p>

<p>Visiting galleries, studios, markets and workshops can offer a different view
of the country. Instead of simply purchasing an object, take time to understand
the person who made it and the ideas or traditions behind the work.</p>

<p>Where possible, buy directly from makers and ask about the origin of products.
Responsible purchasing supports creative livelihoods while helping travellers
take home something connected to a real story.</p>

<h2>Explore Nairobi With Fresh Eyes</h2>

<p>Nairobi is a city of contrasts. Modern businesses, historic neighbourhoods,
creative spaces, restaurants, markets, green areas and cultural institutions
exist alongside one another.</p>

<p>It is easy to treat Nairobi as a starting point before heading elsewhere.
Yet the city can be a destination in its own right.</p>

<p>Spend time exploring its creative spaces. Visit galleries and museums. Discover
local coffee. Look for independent restaurants. Learn about the city's changing
neighbourhoods and the people shaping them.</p>

<h3>Choose Experiences That Invite Participation</h3>

<p>The most rewarding experiences often allow you to do more than observe. Learn
how something is made. Take part in a workshop. Ask questions. Taste something
new. Walk through a neighbourhood with someone who knows it intimately.</p>

<p>Participation creates a different relationship with a destination because you
leave with understanding as well as memories.</p>

<h2>Heritage Lives in Everyday Places</h2>

<p>Heritage is not limited to monuments and museums. It can exist in architecture,
language, music, food, family traditions and the ways communities use public
spaces.</p>

<p>Approach historic places with patience. Read about their significance. Listen
to local perspectives. If photography is involved, be considerate and ask
permission when appropriate.</p>

<p>Understanding context makes a visit richer. A building is more than its walls
when you know why it matters.</p>

<h2>Travel With Respect</h2>

<p>Meaningful cultural travel begins with recognising that the people you meet
are not attractions. They are hosts, professionals, creators, neighbours and
communities with their own lives and perspectives.</p>

<ul>
    <li>Ask permission before photographing people.</li>
    <li>Respect local customs and personal boundaries.</li>
    <li>Support local businesses and independent makers where possible.</li>
    <li>Do not reduce complex cultures to stereotypes.</li>
    <li>Listen before assuming you understand.</li>
    <li>Leave cultural and community spaces with the same respect you brought into them.</li>
</ul>

<p>Responsible cultural travel is ultimately about recognising the difference
between experiencing a place and consuming it.</p>

<h2>Follow Your Curiosity</h2>

<p>You do not need a perfect itinerary to discover something meaningful. A
recommendation from a local, an unexpected café, a small gallery or a
conversation can change the direction of a day.</p>

<p>Leave some room for those moments. They are often the experiences that cannot
be found in a checklist.</p>

<blockquote>
    <p>Travel becomes richer when we stop asking only what a place has to show us
    and start asking what it can teach us.</p>
</blockquote>

<h2>Explore. Experience. Remember.</h2>

<p>Kenya's culture is not contained in a single attraction or a single
experience. It lives across food, art, heritage, craft, conversation and
everyday life.</p>

<p>At The Uncharted Route, we believe meaningful journeys are built around
curiosity, respect and genuine connection with the places we visit.</p>

<p><strong>Come curious. Listen closely. Leave with more than photographs.</strong></p>

<hr>

<p><em>Meet people with respect. Support local creativity. Travel with curiosity.</em></p>
"""


STAYS_CONTENT = """
<h1>The Art of Staying Well: Choosing a Stay That Becomes Part of the Journey</h1>

<p>Where you stay can change the way you experience a destination. A hotel,
residence, lodge or retreat is not simply a place to sleep between activities.
It can shape the pace of your mornings, the way you spend your evenings and the
memories you carry home.</p>

<p><strong>The right stay does more than provide a comfortable room. It gives
the journey a sense of place.</strong></p>

<h2>Choose the Stay Before You Choose the Schedule</h2>

<p>Travel planning often starts with a list of attractions. Yet accommodation
can be just as important, particularly when the purpose of a trip is to rest,
reconnect or experience a destination at a slower pace.</p>

<p>Think about what you want from your stay. Do you want a central city base, a
quiet retreat, a property surrounded by nature or a place where you can spend
most of the day without needing to leave?</p>

<p>Your answer can help determine the right type of accommodation before you
start filling the itinerary with activities.</p>

<h2>Not Every Stay Needs to Be the Same</h2>

<p>Kenya offers a wide range of accommodation experiences. A city hotel can make
a short business or leisure trip convenient. A serviced residence can provide
space and flexibility for a longer stay. A countryside retreat can make the
journey feel slower, while a safari lodge can place the surrounding landscape
at the centre of the experience.</p>

<p>The important question is not simply whether a property looks impressive. It
is whether it suits the way you want to travel.</p>

<h3>For the City Traveller</h3>

<p>A well-positioned city stay can reduce unnecessary travel time and make it
easier to explore restaurants, galleries, business districts and local
experiences.</p>

<p>For longer stays, residences and apartment-style accommodation can offer
additional space, kitchens or living areas that make the experience feel less
like a short hotel visit and more like having a temporary home.</p>

<h3>For the Traveller Seeking Stillness</h3>

<p>A peaceful property can be the destination itself. Gardens, views, wellness
facilities, outdoor spaces and thoughtful dining can create opportunities to
slow down without needing a packed programme.</p>

<p>Sometimes the best plan is to leave an afternoon deliberately empty.</p>

<h2>Look Beyond the Room</h2>

<p>The room matters, but it is only one part of the experience. Consider what
the property offers around it.</p>

<p>Dining, wellness, swimming pools, gardens, fitness facilities, meeting spaces,
family amenities and access to nearby experiences can all influence whether a
stay feels convenient or genuinely enjoyable.</p>

<ul>
    <li>Consider the property's location and surroundings.</li>
    <li>Look at the facilities you are actually likely to use.</li>
    <li>Check dining options and meal arrangements.</li>
    <li>Think about transport and access to nearby experiences.</li>
    <li>Consider whether the property suits your preferred pace of travel.</li>
    <li>Read the booking and cancellation conditions before committing.</li>
</ul>

<p>A long list of facilities is less important than the few things that will
actually improve your journey.</p>

<h2>Let the Destination Influence the Stay</h2>

<p>A stay should make sense within its surroundings. In Nairobi, location and
access can be important because the city is large and different neighbourhoods
offer different experiences.</p>

<p>In the highlands, views and landscape may matter more. At the coast, proximity
to the ocean and the character of the surrounding area can shape the experience.
In a safari destination, the relationship between the property and the
wilderness becomes part of the journey itself.</p>

<p>Think of accommodation as another chapter in the destination's story rather
than a neutral space between activities.</p>

<h2>Slow Travel Is About Attention</h2>

<p>Slow travel does not necessarily mean travelling for weeks. It can mean
changing the way you experience a shorter trip.</p>

<p>Instead of filling every hour, leave room for breakfast without rushing, a
walk around the property, an afternoon by the pool, a quiet conversation or
simply watching the landscape change.</p>

<p>These moments may appear insignificant when planning an itinerary, but they
often become some of the clearest memories afterwards.</p>

<h3>Give Yourself Permission to Do Less</h3>

<p>There is value in returning to your room before sunset, ordering dinner at
the property or spending an hour reading instead of searching for another
activity.</p>

<p>Rest is not wasted travel time. It is part of the experience.</p>

<h2>Choose Places With a Sense of Story</h2>

<p>Some properties stand out because of their architecture or facilities. Others
become memorable because of their history, setting, people or relationship with
the surrounding community.</p>

<p>Look for the details that give a property character. Perhaps it has a
conservation story, a distinctive heritage, a connection to local food or a
landscape that cannot be recreated elsewhere.</p>

<p>These details can turn accommodation into something worth remembering in its
own right.</p>

<h2>Travel Thoughtfully</h2>

<p>Good accommodation choices can also support more responsible travel. Consider
properties that demonstrate care for their environment, employ local people,
work with nearby communities or take meaningful steps towards conservation.</p>

<p>Responsible hospitality looks different from property to property. The
important thing is to look beyond marketing language and consider the actual
relationship between the property, its people and its surroundings.</p>

<blockquote>
    <p>The best stay is not always the one with the longest list of facilities.
    Sometimes it is the place that makes you wish you had booked one more night.</p>
</blockquote>

<h2>Explore. Experience. Remember.</h2>

<p>Travel does not have to be measured by how many places you manage to see. A
well-chosen stay can give a journey breathing room and make the destination
feel more personal.</p>

<p>At The Uncharted Route, we believe accommodation should support the experience
rather than simply sit beside it. Whether you are looking for a refined city
base, a peaceful retreat or a place surrounded by nature, choose somewhere that
fits the story you want your journey to tell.</p>

<p><strong>Stay somewhere that gives you more than a room. Stay somewhere that
becomes part of the memory.</strong></p>

<hr>

<p><em>Slow down. Stay well. Let the place become part of your journey.</em></p>
"""


# =============================================================================
# PLANNED POSTS
# =============================================================================

PLANNED_POSTS = [
    {
        "title": "Kenya Beyond the Obvious: Places Worth Taking Your Time To Discover",
        "slug": "kenya-beyond-the-obvious-places-worth-discovering",
        "subtitle": (
            "A slower look at the landscapes, escapes and destinations "
            "that make Kenya worth discovering beyond the familiar."
        ),
        "excerpt": (
            "Kenya is more than its famous safari destinations. Discover how "
            "coastal escapes, highland retreats, local landscapes and slower "
            "journeys can reveal another side of the country."
        ),
        "category_slug": "destinations-getaways",
        "content": DESTINATIONS_CONTENT,
        "featured_image": None,
        "featured_image_alt": None,
        "related_experience_id": None,
        "related_destination_id": None,
        "cta_title": "Find Your Next Kenyan Escape",
        "cta_text": (
            "Explore thoughtfully selected destinations and experiences "
            "designed around how you want to travel."
        ),
        "cta_button_text": "Explore Destinations",
        "cta_button_url": "/destinations/",
        "meta_title": (
            "Kenya Beyond the Obvious | Destinations & Getaways | "
            "The Uncharted Route"
        ),
        "meta_description": (
            "Discover a slower side of Kenya through coastal escapes, "
            "highland retreats, nature destinations and journeys worth "
            "taking your time to experience."
        ),
        "meta_keywords": (
            "Kenya destinations, Kenya getaways, coastal escapes, "
            "highland retreats, Kenya travel, slow travel, "
            "The Uncharted Route"
        ),
        "social_title": (
            "Kenya Beyond the Obvious: Places Worth Taking Your Time To Discover"
        ),
        "social_description": (
            "A slower look at the landscapes, escapes and destinations "
            "that make Kenya worth discovering."
        ),
        "social_image": None,
        "featured": True,
        "pinned": False,
        "allow_comments": True,
    },
    {
        "title": "Beyond the Guidebook: Discovering Kenya Through Local Experiences",
        "slug": "beyond-the-guidebook-discovering-kenya-through-local-experiences",
        "subtitle": (
            "Food, craft, heritage, creativity and everyday encounters "
            "can reveal a deeper side of Kenya."
        ),
        "excerpt": (
            "Discover Kenya through the people, food, craft, heritage and "
            "creative spaces that bring destinations to life beyond the "
            "traditional sightseeing itinerary."
        ),
        "category_slug": "culture-local-experiences",
        "content": CULTURE_CONTENT,
        "featured_image": None,
        "featured_image_alt": None,
        "related_experience_id": None,
        "related_destination_id": 1,
        "cta_title": "Discover Kenya Differently",
        "cta_text": (
            "Explore meaningful experiences rooted in culture, creativity, "
            "food and local discovery."
        ),
        "cta_button_text": "Explore Experiences",
        "cta_button_url": "/experiences/",
        "meta_title": (
            "Discover Kenya Through Local Experiences | "
            "The Uncharted Route"
        ),
        "meta_description": (
            "Explore Kenyan culture through food, craft, heritage, "
            "creativity and meaningful local experiences with "
            "The Uncharted Route."
        ),
        "meta_keywords": (
            "Kenyan culture, local experiences Kenya, Kenyan food, "
            "Kenyan heritage, Nairobi culture, cultural travel, "
            "The Uncharted Route"
        ),
        "social_title": (
            "Beyond the Guidebook: Discovering Kenya Through Local Experiences"
        ),
        "social_description": (
            "Discover Kenya through food, craft, heritage, creativity "
            "and everyday local experiences."
        ),
        "social_image": None,
        "featured": True,
        "pinned": False,
        "allow_comments": True,
    },
    {
        "title": "The Art of Staying Well: Choosing a Stay That Becomes Part of the Journey",
        "slug": "the-art-of-staying-well-choosing-a-stay",
        "subtitle": (
            "Why the right hotel, residence, lodge or retreat can shape "
            "the pace and memory of an entire journey."
        ),
        "excerpt": (
            "The right stay can be more than a place to sleep. Discover how "
            "location, atmosphere, facilities and a slower pace can turn "
            "accommodation into part of the travel experience."
        ),
        "category_slug": "stays-slow-travel",
        "content": STAYS_CONTENT,
        "featured_image": None,
        "featured_image_alt": None,
        "related_experience_id": None,
        "related_destination_id": None,
        "cta_title": "Find a Stay Worth Remembering",
        "cta_text": (
            "Discover considered stays and accommodation experiences "
            "that complement the way you want to travel."
        ),
        "cta_button_text": "Explore Stays",
        "cta_button_url": "/stays/",
        "meta_title": (
            "The Art of Staying Well | Stays & Slow Travel | "
            "The Uncharted Route"
        ),
        "meta_description": (
            "Discover how choosing the right stay can shape your journey "
            "through location, atmosphere, comfort and slower travel."
        ),
        "meta_keywords": (
            "Kenya stays, Kenya hotels, boutique stays, slow travel, "
            "Kenya retreats, luxury stays Kenya, "
            "The Uncharted Route"
        ),
        "social_title": (
            "The Art of Staying Well: Choosing a Stay That Becomes Part of the Journey"
        ),
        "social_description": (
            "Why the right hotel, residence, lodge or retreat can become "
            "part of the journey itself."
        ),
        "social_image": None,
        "featured": True,
        "pinned": False,
        "allow_comments": True,
    },
]


# =============================================================================
# DATABASE LOOKUPS
# =============================================================================

def get_category_by_slug(slug: str):
    return (
        BlogCategory.query
        .filter(BlogCategory.slug == slug)
        .first()
    )


def get_existing_post(post_data):
    """
    Find an existing post by slug first, then title.

    Existing posts are never modified.
    """

    post = (
        BlogPost.query
        .filter(BlogPost.slug == post_data["slug"])
        .first()
    )

    if post is not None:
        return post

    return (
        BlogPost.query
        .filter(BlogPost.title == post_data["title"])
        .first()
    )


# =============================================================================
# VALIDATION
# =============================================================================

def validate_categories():
    required_slugs = {
        "safari-wildlife",
        "destinations-getaways",
        "culture-local-experiences",
        "stays-slow-travel",
    }

    categories = {}

    for slug in required_slugs:
        category = get_category_by_slug(slug)

        if category is None:
            raise RuntimeError(
                f"Required BlogCategory does not exist: {slug}"
            )

        if not category.active:
            raise RuntimeError(
                f"Required BlogCategory is inactive: "
                f"{category.name} ({category.slug})"
            )

        categories[slug] = category

    return categories


def validate_existing_catalogue():
    """
    Validate the current BlogPost catalogue without changing anything.

    The existing launch post must remain present.
    """

    existing_posts = BlogPost.query.all()

    print()
    print("CURRENT BLOG CATALOGUE")
    print(f"    Existing posts: {len(existing_posts)}")

    for post in existing_posts:
        print(
            f"    - #{post.id}: {post.title} "
            f"[{post.status}] "
            f"[{post.slug}]"
        )

    if len(existing_posts) != 1:
        print()
        print(
            "WARNING: The current catalogue does not contain exactly one "
            "existing BlogPost."
        )
        print(
            "The script will still protect every existing post and will "
            "only create missing planned posts."
        )

    existing_reference = (
        BlogPost.query
        .filter(
            BlogPost.slug
            == "the-wild-at-your-doorstep-nairobi-national-park"
        )
        .first()
    )

    if existing_reference is None:
        raise RuntimeError(
            "The expected existing launch post was not found: "
            "'The Wild at Your Doorstep: Discovering the Magic of "
            "Nairobi National Park'."
        )

    print()
    print("EXISTING LAUNCH POST PROTECTION")
    print(
        f"    ID     : {existing_reference.id}"
    )
    print(
        f"    Title  : {existing_reference.title}"
    )
    print(
        f"    Slug   : {existing_reference.slug}"
    )
    print(
        f"    Status : {existing_reference.status}"
    )
    print(
        "    Action : PRESERVE — no update/delete/duplicate"
    )

    return existing_reference


def validate_planned_posts(categories):
    print()
    print("PLANNED NEW POSTS")

    for post_data in PLANNED_POSTS:
        category = categories.get(post_data["category_slug"])

        if category is None:
            raise RuntimeError(
                f"Category resolution failed: "
                f"{post_data['category_slug']}"
            )

        if not post_data["content"].strip():
            raise RuntimeError(
                f"Post content is empty: {post_data['title']}"
            )

        if not post_data["slug"]:
            raise RuntimeError(
                f"Post slug is empty: {post_data['title']}"
            )

        word_count = calculate_word_count(post_data["content"])
        reading_time = calculate_reading_time(post_data["content"])

        print()
        print(f"    {post_data['title']}")
        print(f"        Slug         : {post_data['slug']}")
        print(f"        Category     : {category.name}")
        print(f"        Word count   : {word_count}")
        print(f"        Reading time : {reading_time} min")
        print(f"        Status       : {STATUS_PUBLISHED}")

    print()


# =============================================================================
# DRY-RUN
# =============================================================================

def run_dry_run(categories):
    print()
    print(SEPARATOR)
    print("DRY RUN — NO DATABASE CHANGES")
    print(SEPARATOR)

    existing_count = BlogPost.query.count()

    would_create = 0
    would_reuse = 0

    for post_data in PLANNED_POSTS:
        existing = get_existing_post(post_data)
        category = categories[post_data["category_slug"]]

        print()
        print(SUB_SEPARATOR)
        print(post_data["title"])
        print(SUB_SEPARATOR)

        print(f"Category       : {category.name}")
        print(f"Slug           : {post_data['slug']}")
        print(f"Status         : {STATUS_PUBLISHED}")

        if existing:
            would_reuse += 1

            print()
            print("ACTION         : REUSE / PRESERVE")
            print(f"Existing ID    : {existing.id}")
            print(
                "Existing record will NOT be updated."
            )
        else:
            would_create += 1

            word_count = calculate_word_count(
                post_data["content"]
            )
            reading_time = calculate_reading_time(
                post_data["content"]
            )

            print()
            print("ACTION         : CREATE")
            print(f"Word Count     : {word_count}")
            print(f"Reading Time   : {reading_time} min")
            print(
                "Media          : No new media record"
            )
            print(
                "Engagement     : No fabricated views/likes/shares"
            )
            print(
                "Newsletter     : newsletter_sent=False"
            )

    print()
    print(SEPARATOR)
    print("DRY-RUN SUMMARY")
    print(SEPARATOR)

    print(f"Existing posts             : {existing_count}")
    print(f"Planned posts              : {len(PLANNED_POSTS)}")
    print(f"Posts already present      : {would_reuse}")
    print(f"Posts that would be created: {would_create}")
    print(
        f"Expected final total       : "
        f"{existing_count + would_create}"
    )

    print()
    print(
        "Expected launch catalogue:"
    )

    all_posts = BlogPost.query.order_by(BlogPost.id.asc()).all()

    for post in all_posts:
        print(
            f"    EXISTING  #{post.id}: {post.title}"
        )

    for post_data in PLANNED_POSTS:
        existing = get_existing_post(post_data)

        if existing:
            print(
                f"    EXISTING  #{existing.id}: {existing.title}"
            )
        else:
            print(
                f"    NEW       {post_data['title']}"
            )

    if existing_count + would_create != EXPECTED_FINAL_POST_COUNT:
        print()
        print(
            "WARNING: Final post count will not equal the expected "
            f"{EXPECTED_FINAL_POST_COUNT}."
        )

    print()
    print(
        "No database mutation has occurred."
    )
    print(
        "Use --apply to create only the missing posts."
    )


# =============================================================================
# POST CREATION
# =============================================================================

def build_blog_post(post_data, category):
    """
    Construct a new BlogPost without flushing or committing.
    """

    content = post_data["content"].strip()

    word_count = calculate_word_count(content)
    reading_time = calculate_reading_time(content)

    post = BlogPost(
        category_id=category.id,
        title=post_data["title"],
        slug=post_data["slug"],
        subtitle=post_data["subtitle"],
        excerpt=post_data["excerpt"],
        content=content,
        author=AUTHOR_NAME,
        author_title=AUTHOR_TITLE,
        author_photo=None,
        featured_image=post_data["featured_image"],
        featured_image_alt=post_data["featured_image_alt"],
        cover_video=None,
        gallery=None,
        reading_time=reading_time,
        word_count=word_count,
        status=STATUS_PUBLISHED,
        published_at=datetime.utcnow(),
        scheduled_for=None,
        featured=post_data["featured"],
        pinned=post_data["pinned"],
        allow_comments=post_data["allow_comments"],
        related_experience_id=post_data["related_experience_id"],
        related_destination_id=post_data["related_destination_id"],
        cta_title=post_data["cta_title"],
        cta_text=post_data["cta_text"],
        cta_button_text=post_data["cta_button_text"],
        cta_button_url=post_data["cta_button_url"],
        meta_title=post_data["meta_title"],
        meta_description=post_data["meta_description"],
        meta_keywords=post_data["meta_keywords"],
        canonical_url=None,
        social_title=post_data["social_title"],
        social_description=post_data["social_description"],
        social_image=post_data["social_image"],
        views=0,
        likes=0,
        shares=0,
        newsletter_sent=False,
        search_indexed=False,
    )

    return post


# =============================================================================
# APPLY
# =============================================================================

def apply_population(categories):
    print()
    print(SEPARATOR)
    print("APPLY — BLOG CATALOGUE POPULATION")
    print(SEPARATOR)

    created = []
    reused = []

    try:
        for post_data in PLANNED_POSTS:
            existing = get_existing_post(post_data)

            if existing:
                reused.append(existing)

                print()
                print(
                    f"REUSED / PRESERVED: #{existing.id} "
                    f"{existing.title}"
                )
                print(
                    "    No fields modified."
                )

                continue

            category = categories[post_data["category_slug"]]

            post = build_blog_post(
                post_data,
                category,
            )

            db.session.add(post)

            # Flush only to obtain the generated primary key.
            db.session.flush()

            created.append(post)

            print()
            print(
                f"CREATED: #{post.id} "
                f"{post.title}"
            )
            print(
                f"    Category     : {category.name}"
            )
            print(
                f"    Slug         : {post.slug}"
            )
            print(
                f"    Status       : {post.status}"
            )
            print(
                f"    Word Count   : {post.word_count}"
            )
            print(
                f"    Reading Time : {post.reading_time} min"
            )

        db.session.commit()

    except Exception:
        db.session.rollback()

        print()
        print(SEPARATOR)
        print("POPULATION FAILED")
        print(SEPARATOR)
        print(
            "The transaction has been rolled back."
        )
        print(
            "No partial changes were committed."
        )

        raise

    final_count = BlogPost.query.count()

    print()
    print(SEPARATOR)
    print("POPULATION COMPLETE")
    print(SEPARATOR)

    print(f"Posts created       : {len(created)}")
    print(f"Posts preserved     : {len(reused)}")
    print(f"Final BlogPost total: {final_count}")

    print()
    print("EXISTING CONTENT")
    print(
        "    The original Nairobi National Park article was preserved."
    )

    print()
    print("MEDIA")
    print(
        "    New media records created: 0"
    )

    print()
    print("ENGAGEMENT")
    print(
        "    Views/likes/shares fabricated: 0"
    )

    print()
    print("NEWSLETTER")
    print(
        "    Newsletter activity created: 0"
    )

    if final_count != EXPECTED_FINAL_POST_COUNT:
        print()
        print(
            "WARNING: Final BlogPost total is "
            f"{final_count}, expected {EXPECTED_FINAL_POST_COUNT}."
        )

    return created, reused


# =============================================================================
# FINAL CATALOGUE REPORT
# =============================================================================

def print_final_catalogue():
    print()
    print(SEPARATOR)
    print("FINAL BLOG CATALOGUE")
    print(SEPARATOR)

    posts = (
        BlogPost.query
        .order_by(
            BlogPost.category_id.asc(),
            BlogPost.id.asc(),
        )
        .all()
    )

    for post in posts:
        category_name = (
            post.category.name
            if post.category
            else "UNKNOWN CATEGORY"
        )

        print()
        print(
            f"#{post.id} — {post.title}"
        )
        print(
            f"    Category : {category_name}"
        )
        print(
            f"    Slug     : {post.slug}"
        )
        print(
            f"    Status   : {post.status}"
        )
        print(
            f"    Featured : {'YES' if post.featured else 'NO'}"
        )

    print()
    print(
        f"TOTAL POSTS: {len(posts)}"
    )


# =============================================================================
# CLI
# =============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Populate the initial The Uncharted Route Blog catalogue."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Apply the Blog catalogue population. "
            "Without this flag the script performs a read-only dry run."
        ),
    )

    return parser.parse_args()


# =============================================================================
# MAIN
# =============================================================================

def main():
    args = parse_args()

    app = create_population_app()

    with app.app_context():
        print()
        print(SEPARATOR)
        print("THE UNCHARTED ROUTE — BLOG CATALOGUE POPULATION")
        print(SEPARATOR)

        print()
        print(
            "Mode:",
            "APPLY" if args.apply else "DRY RUN",
        )

        print()
        print(
            "Safety rules:"
        )
        print(
            "    - Existing BlogPosts are preserved."
        )
        print(
            "    - Existing BlogCategories are reused."
        )
        print(
            "    - Only three missing launch posts are planned."
        )
        print(
            "    - No new media records."
        )
        print(
            "    - No fabricated engagement."
        )
        print(
            "    - No newsletter activity."
        )

        categories = validate_categories()

        validate_existing_catalogue()

        validate_planned_posts(categories)

        if not args.apply:
            run_dry_run(categories)
            return

        apply_population(categories)

        print_final_catalogue()

        print()
        print(SEPARATOR)
        print("BLOG CATALOGUE POPULATION FINISHED")
        print(SEPARATOR)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print()
        print(SEPARATOR)
        print("ERROR")
        print(SEPARATOR)
        print(str(exc))
        print()
        sys.exit(1)