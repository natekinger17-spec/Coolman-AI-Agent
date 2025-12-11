"""
Coolman Fuels Customer Support AI Agent
========================================
An intelligent AI agent providing 24/7 customer support for Coolman Fuels.
Handles inquiries about fuel delivery, propane services, pricing, coverage areas,
and general account questions with comprehensive knowledge of company operations.

Version: 1.0
Last Updated: December 2025
"""

import asyncio
from typing import Annotated
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI

# ============================================================================
# COOLMAN FUELS KNOWLEDGE BASE
# ============================================================================

COMPANY_INFO = {
    "name": "Coolman Fuels",
    "formerly_known_as": "Dave Moore Fuels",
    "established": 1976,
    "type": "Family-owned company",
    "location": "71321 London Road, Exeter, ON N0M 1S3",
    "phone": "+1 519-235-0853",
    "email": "sales@coolmanfuels.ca",
    "website": "https://www.coolmanfuels.ca",
    "hours": "24/7 availability",
    "delivery": "Automatic degree day delivery available",
    "cardlock_locations": ["Exeter", "Mitchell"],
    "partnerships": {
        "propane_delivery": {
            "partner": "Core Fuels Ltd / Red Cap Propane Ltd",
            "partner_phone": "519-272-0090",
            "partner_email": "info@corefuels.ca",
            "partner_website": "https://www.corefuels.ca",
            "partner_location": "219 Lorne Ave. E., Stratford, ON N5A 6S4",
            "partner_established": 1972,
            "partnership_since": 2004,
            "arrangement": "Red Cap Propane handles propane delivery for Coolman Fuels customers in Lambton, Middlesex, and Huron Counties; Coolman handles furnace oil delivery for Core Fuels customers",
            "note": "Coolman Fuels does not operate a propane truck - propane orders are fulfilled by Red Cap Propane (Core Fuels)",
            "partner_motto": "Quality products and great service at a fair price",
            "partner_history": "Family-owned since 1972, operated by James and Kevin Core. Red Cap Propane established in 2004."
        }
    },
    "tank_inspection_requirements": {
        "description": "For new propane, furnace oil, or generator delivery accounts, a comprehensive oil inspection by a licensed technician is required before we can begin deliveries.",
        "recommended_inspectors": [
            {
                "name": "Avon Heating",
                "phone": "519-348-0514",
                "website": "https://www.avonheating.ca",
                "primary_recommendation": True
            },
            {
                "name": "Rob Lynn / Town & Country",
                "phone": "519-878-0954",
                "email": "roblynn@quadro.net",
                "primary_recommendation": False
            }
        ]
    }
}

# Detailed service area information based on actual territory
SERVICE_TERRITORY = {
    "primary_communities": [
        "Exeter",       # HQ - center of territory
        "Mitchell",     # Cardlock location, eastern boundary
        "Goderich",     # Northern boundary - Lake Huron
        "Grand Bend",   # Western boundary - Lake Huron shore
        "Thedford",     # Southern-western boundary
        "Parkhill",     # South-central
        "Dublin",       # Central-east
        "Lucan Biddulph", # Southern boundary
        "Seaforth",     # North-central
        "Clinton",      # North-central (west of Seaforth)
        "Bayfield",     # Lake Huron shore
        "Blyth",        # Northern area
        "Walton",       # North-east of Exeter
        "Staffa",       # East of Exeter
        "Kippen",       # West of Exeter
        "Centralia",    # South of Exeter
        "Crediton",     # West of Exeter
        "Arkona",       # South-west near Thedford
        "Granton",      # South-east
        "Clandeboye",   # South
        "Forest",       # South-west
        "Dashwood",     # West of Exeter
        "Hensall",      # North-east
        "Zurich",       # West
        "Varna",        # North-west
        "Brucefield",   # North
        "Holmesville",  # North
        "Auburn",       # North near Blyth
    ],
    "boundary_communities": [
        # These are on the edge of our service area
        "Ilderton",     # South - close to London
        "Ailsa Craig",  # South-east
        "St. Marys",    # East boundary
        "Stratford",    # East - call to confirm
        "Wingham",      # North boundary
        "London (North)", # South boundary - call to confirm
    ],
    "counties_served": [
        "Huron County (southern portion)",
        "Perth County (western portion)", 
        "Middlesex County (northern portion)",
        "Lambton County (eastern portion)",
    ],
    "boundaries": {
        "north": "Goderich to Wingham area (Highway 8/21 corridor)",
        "east": "Mitchell to St. Marys line (Perth Road 163, Highway 7/19)",
        "south": "Lucan to London boundary (Highway 4 corridor)",
        "west": "Lake Huron shoreline from Goderich to Thedford",
    },
    # Internal territory reference - not shared with customers
    "approximate_coverage_km2": 2500,
    "service_radius_km": 40,  # From Exeter HQ
}

PRODUCTS = {
    "regular_gasoline": {
        "name": "Regular Gasoline",
        "description": "Top-notch gasoline for gas-powered vehicles",
        "delivery": "Available for on-site delivery",
        "category": "fuel",
        "typical_tank_sizes": {
            "standard": "300-500 gallons (1,135-1,890 litres)",
            "large_operations": "1,000+ gallons (3,785+ litres) for very large operations"
        }
    },
    "clear_diesel": {
        "name": "Clear Diesel",
        "description": "Used for road vehicles such as transport trucks",
        "category": "fuel",
        "typical_tank_sizes": {
            "standard": "300-500 gallons (1,135-1,890 litres)",
            "large_operations": "1,000+ gallons (3,785+ litres) for very large operations"
        }
    },
    "dyed_diesel": {
        "name": "Dyed Diesel",
        "description": "Used for off-road trucks such as tractors and construction equipment",
        "category": "fuel",
        "typical_tank_sizes": {
            "standard": "300-500 gallons (1,135-1,890 litres)",
            "large_operations": "1,000+ gallons (3,785+ litres) for very large operations"
        }
    },
    "heating_oil": {
        "name": "Heating Oil",
        "description": "For house furnaces, mainly used for rural homes",
        "category": "residential",
        "typical_tank_size": "900L (only mention if customer asks)"
    },
    "propane": {
        "name": "Propane",
        "description": "For residential use, mainly for rural farms",
        "brand": "Red Cap Propane",
        "uses": ["Home heating", "Water heating", "Cooking", "Fireplaces", "Clothes dryers", "Crop drying"],
        "category": "residential",
        "delivery_partner": "Red Cap Propane Ltd (Core Fuels) - our propane partner since 2004",
        "partner_phone": "519-272-0090"
    },
    "lubricants": {
        "name": "Petro-Canada™ Lubricants",
        "description": "Superior quality lubricants for various industries",
        "industries": ["On-highway vehicles", "Agriculture", "Construction", "Mining"],
        "website": "https://petrocanadalubricants.com/en-ca/knowledge-centre/product-selector",
        "category": "commercial"
    },
    "def": {
        "name": "DEF (Diesel Exhaust Fluid)",
        "description": "DEF for commercial diesel vehicles - reduces emissions and keeps engines running clean",
        "category": "commercial",
        "brands": {
            "bulk": "Air1 (API certified, ISO 22241)",
            "jugs": "Catalys (10L)"
        },
        "availability": {
            "bulk_delivery": "Available for farmers and commercial customers",
            "jugs_10L": "Catalys brand 10L jugs available",
            "drums": "Available if ordered 1-2 weeks in advance",
            "cardlock_pumps": "Coming Spring 2026 - not yet available at our pumps"
        }
    },
    "specialty_fluids": {
        "name": "Specialty Fluids",
        "description": "Antifreeze and washer fluid",
        "category": "commercial"
    }
}

SERVICES = {
    "bulk_storage_delivery": {
        "name": "Bulk Storage Delivery",
        "description": "Fuel delivered directly to your site for consistent energy supply"
    },
    "in_yard_delivery": {
        "name": "In-Yard Delivery",
        "description": "Fuel delivered directly to your location for convenience"
    },
    "into_equipment_fueling": {
        "name": "Into-Equipment Fueling",
        "description": "Direct-to-equipment fueling at your location",
        "advertise": False,
        "note": "Available by request only - call to discuss"
    },
    "cardlock_fueling": {
        "name": "On-Site Cardlock Fueling",
        "description": "Secure, 24/7 self-serve fueling stations"
    },
    "equipment_rentals": {
        "name": "Equipment Rentals",
        "description": "Tanks, fuel pumps, and lubricant equipment rentals and installations"
    },
    "automatic_delivery": {
        "name": "Automatic Delivery",
        "description": "Never run out guarantee with automatic delivery"
    },
    "on_demand_delivery": {
        "name": "On-Demand Delivery",
        "description": "Schedule deliveries with 24-48 hours notice"
    },
    "emergency_delivery": {
        "name": "Emergency Delivery",
        "description": "We always have a driver on call for emergency deliveries when absolutely needed",
        "note": "Use of emergency delivery after hours may result in a delivery fee if abused or misused"
    }
}

FLEET_CARDS = {
    "petro_pass": {
        "name": "Petro-Pass™ Cardlock",
        "description": "Access to over 300 locations nationwide along major routes across Canada",
        "features": ["High-speed diesel fueling", "Canada's largest national cardlock network"]
    },
    "compatible_cards": ["BVD Petroleum card", "US-based Comdata", "EFS card"],
    "ipn_access": "Access to over 60 cardlock locations throughout Ontario via Independent Petroleum Network"
}

INDUSTRIES_SERVED = [
    "Agriculture", "Construction", "Transportation", 
    "Mining & Forestry", "Manufacturing", "Aviation", "Marine"
]

# ============================================================================
# AGENT TOOLS - Functions the AI can use to help customers
# ============================================================================

def get_company_info() -> str:
    """Get general information about Coolman Fuels company."""
    primary_areas = ", ".join(SERVICE_TERRITORY['primary_communities'][:10])
    return f"""
    **Coolman Fuels** (formerly {COMPANY_INFO['formerly_known_as']})
    - Family-owned since {COMPANY_INFO['established']}
    - Location: {COMPANY_INFO['location']}
    - Phone: {COMPANY_INFO['phone']}
    - Email: {COMPANY_INFO['email']}
    - Website: {COMPANY_INFO['website']}
    - Hours: {COMPANY_INFO['hours']} with {COMPANY_INFO['delivery']}
    
    Primary Service Areas: {primary_areas}, and many more communities
    Cardlock Locations: {', '.join(COMPANY_INFO['cardlock_locations'])}
    Coverage: ~{SERVICE_TERRITORY['approximate_coverage_km2']} km² across Huron, Perth, Middlesex, and Lambton counties
    """

def get_products_list(
    category: Annotated[str, "Product category: 'all', 'fuel', 'residential', or 'commercial'"] = "all"
) -> str:
    """Get a list of products offered by Coolman Fuels, optionally filtered by category."""
    result = "**Coolman Fuels Products:**\n\n"
    
    for key, product in PRODUCTS.items():
        if category == "all" or product.get("category", "") == category:
            result += f"- **{product['name']}**: {product['description']}\n"
            if "brand" in product:
                result += f"  - Brand: {product['brand']}\n"
            if "uses" in product:
                result += f"  - Uses: {', '.join(product['uses'])}\n"
    
    return result

def get_services_list(
    service_type: Annotated[str, "Service type: 'all', 'delivery', or 'payment'"] = "all"
) -> str:
    """Get a list of services offered by Coolman Fuels."""
    result = "**Coolman Fuels Services:**\n\n"
    
    delivery_services = ["bulk_storage_delivery", "in_yard_delivery", 
                        "cardlock_fueling", "automatic_delivery", "on_demand_delivery"]
    payment_services = ["equal_payment"]
    
    for key, service in SERVICES.items():
        if service_type == "all":
            include = True
        elif service_type == "delivery":
            include = key in delivery_services
        elif service_type == "payment":
            include = key in payment_services
        else:
            include = True
            
        if include:
            result += f"- **{service['name']}**: {service['description']}\n"
    
    return result

def get_contact_info() -> str:
    """Get contact information for Coolman Fuels."""
    return f"""
    **Contact Coolman Fuels:**
    
    📍 Address: {COMPANY_INFO['location']}
    📞 Phone: {COMPANY_INFO['phone']}
    ✉️ Email: {COMPANY_INFO['email']}
    🌐 Website: {COMPANY_INFO['website']}
    
    **Hours:** {COMPANY_INFO['hours']}
    
    **Furnace Oil Customers:** Give us a call if you'd like to be set up for degree day automatic deliveries!
    
    To place an order or set up automatic delivery, call us at {COMPANY_INFO['phone']}
    """

def check_service_area(
    location: Annotated[str, "The city or town to check for service availability"]
) -> str:
    """Check if a location is within Coolman Fuels' service area using detailed territory data."""
    location_lower = location.lower().strip()
    
    # Check primary service communities
    primary_lower = [area.lower() for area in SERVICE_TERRITORY['primary_communities']]
    boundary_lower = [area.lower() for area in SERVICE_TERRITORY['boundary_communities']]
    
    # Check for exact or partial matches
    is_primary = any(location_lower in area or area in location_lower for area in primary_lower)
    is_boundary = any(location_lower in area or area in location_lower for area in boundary_lower)
    
    if is_primary:
        return f"""✅ **Great news! {location} is within our PRIMARY service area!**

We provide full delivery service to {location} including:
• Residential: Propane, heating oil
• Commercial: Diesel (clear & dyed), gasoline, lubricants, DEF
• Automatic degree day delivery (give us a call to set this up!)
• Never Run Out Guarantee when you sign up for automatic delivery

💡 **Tip:** It's best to schedule at least one day in advance. We're here to ensure you never run out of fuel! Same-day delivery is only available for emergencies.

📞 Call us at {COMPANY_INFO['phone']} to schedule a delivery!
"""
    
    elif is_boundary:
        return f"""🔄 **{location} - Let's confirm your service!**

This area is on the edge of our regular delivery routes:
• We may be able to serve you depending on your exact location
• Same great Petro-Canada products available
• Potential for scheduled delivery routes

💡 **Tip:** Please call us in advance to schedule your delivery.

📞 Call us at {COMPANY_INFO['phone']} to confirm service for your specific address!
"""
    
    else:
        return f"""📍 **{location} is outside our service area.**

We serve Southwestern Ontario including:
{', '.join(SERVICE_TERRITORY['primary_communities'][:10])}, and surrounding areas.

**Find your nearest Petro-Canada marketer:**
🔗 https://www.petro-canada.ca/en/business/find-a-marketer

**For propane in the Stratford/Perth County area:**
Our partner Core Fuels / Red Cap Propane may be able to help!
📞 519-272-0090 | 🔗 corefuels.ca
"""

def get_service_area_details() -> str:
    """Get detailed information about Coolman Fuels' service territory and boundaries."""
    primary = ", ".join(SERVICE_TERRITORY['primary_communities'][:15])
    boundary = ", ".join(SERVICE_TERRITORY['boundary_communities'])
    counties = ", ".join(SERVICE_TERRITORY['counties_served'])
    
    return f"""
**🗺️ Coolman Fuels Service Territory**

**Your Trusted Petro-Canada Branded Distributor**

**Coverage:** ~{SERVICE_TERRITORY['approximate_coverage_km2']} km² | ~{SERVICE_TERRITORY['service_radius_km']}km radius from Exeter HQ

**Primary Communities We Serve:**
{primary}, and more...

**Counties Served:**
{counties}

**Our Territory:**
• **North:** {SERVICE_TERRITORY['boundaries']['north']}
• **East:** {SERVICE_TERRITORY['boundaries']['east']}
• **South:** {SERVICE_TERRITORY['boundaries']['south']}
• **West:** {SERVICE_TERRITORY['boundaries']['west']}

**Cardlock Locations:** Exeter & Mitchell (24/7 Petro-Pass access)

**Extended Service Areas (call to confirm):**
{boundary}

✨ As a Petro-Canada branded distributor, we offer top-quality fuels backed by a trusted national brand!

📞 Questions about your area? Call {COMPANY_INFO['phone']}
"""

def get_fleet_card_info() -> str:
    """Get information about fleet cards and cardlock fueling."""
    return f"""
    **Fleet Cards & Cardlock Fueling:**
    
    **Petro-Pass™ Cardlock:**
    - Access to 300+ locations nationwide across Canada
    - High-speed diesel fueling
    - Canada's largest national cardlock network
    
    **Compatible Cards:** {', '.join(FLEET_CARDS['compatible_cards'])}
    
    **Local Cardlock Sites:** Exeter and Mitchell
    - Clear diesel, dyed diesel, and gasoline at select sites
    - Part of the Independent Petroleum Network (60+ Ontario locations)
    - *DEF at the pump coming Spring 2026*
    
    Learn more: https://www.petro-canada.ca/en/business/superpass-fleet-management-fuel-card
    
    **Compatible External Cards:** You can also use compatible cards like BVD Petroleum card, US-based Comdata, and EFS card at our locations.
    """

def get_residential_heating_info() -> str:
    """Get information about residential heating solutions (propane and heating oil)."""
    return """
    **Residential Heating Solutions:**
    
    🔥 **Propane** (Red Cap Propane)
    - Consistent, cozy warmth
    - Energy efficient and environmentally friendly
    - Works during power outages
    - Uses: Heating, water heating, cooking, fireplaces, clothes dryers
    - *Propane delivery fulfilled by our partner Red Cap Propane Ltd (Core Fuels)*
    
    🏠 **Heating Oil / Furnace Oil**
    - Dependable heating during cold months
    - High energy density for cost-effective performance
    - Flexibility to choose your supplier
    
    **Home Comfort Services:**
    - ✅ Never Run Out Guarantee
    - 📦 Automatic Degree Day Delivery (give us a call to set this up!)
    - 📅 Scheduled Delivery (it's best to schedule at least one day in advance)
    - 🚨 Emergency Delivery (driver always on call when absolutely needed - may incur a fee if misused)
    
    **⚠️ New Customers - Tank Inspection Required:**
    For new propane, furnace oil, or generator delivery accounts, a comprehensive oil inspection 
    by a licensed technician is required before we can begin deliveries.
    
    **Recommended Inspectors:**
    1. **Avon Heating** (Recommended) - 📞 519-348-0514 | 🌐 https://www.avonheating.ca
    2. **Rob Lynn / Town & Country** - 📞 519-878-0954 | ✉️ roblynn@quadro.net
    
    Once we receive your tank inspection report, we can set you up for deliveries!
    
    📞 Contact us for propane OR heating oil: +1 519-235-0853 or sales@coolmanfuels.ca
    """

def get_new_customer_requirements() -> str:
    """Get information about requirements for new propane, furnace oil, or generator delivery accounts."""
    return """
    **New Customer Requirements - Tank Inspection:**
    
    ⚠️ For new propane, furnace oil, or generator delivery accounts, a **comprehensive oil inspection** 
    by a licensed technician is required before we can begin deliveries.
    
    **Recommended Licensed Inspectors:**
    
    1️⃣ **Avon Heating** (Our Primary Recommendation)
       📞 Phone: 519-348-0514
       🌐 Website: https://www.avonheating.ca
    
    2️⃣ **Rob Lynn / Town & Country**
       📞 Phone: 519-878-0954
       ✉️ Email: roblynn@quadro.net
    
    **What happens next:**
    1. Contact one of the recommended inspectors to schedule your tank inspection
    2. Once the inspection is complete, send us the inspection report
    3. We'll set you up as a customer and begin deliveries!
    
    📞 Questions? Call us at +1 519-235-0853 or email sales@coolmanfuels.ca
    """

def get_commercial_solutions() -> str:
    """Get information about commercial fuel solutions."""
    industries = ', '.join(INDUSTRIES_SERVED)
    return f"""
    **Commercial Fuel Solutions:**
    
    **Industries We Serve:** {industries}
    
    **Fuel Products:**
    - Clear & Dyed Diesel
    - Regular Gasoline
    
    **DEF (Diesel Exhaust Fluid):**
    - 📦 **Bulk DEF** - delivered to farmers & commercial customers
    - 🧴 **10L Jugs** (Catalys brand) - available now
    - 🛢️ **Drums** - available if ordered 1-2 weeks in advance
    - ⛽ *DEF at the pump coming Spring 2026*
    
    **Lubricants:**
    - Petro-Canada™ Lubricants (packaged or bulk delivery)
    - Product selector: https://petrocanadalubricants.com/en-ca/knowledge-centre/product-selector
    
    **Delivery Services:**
    - Bulk Storage Delivery
    - In-Yard Delivery
    - 24/7 Cardlock Fueling
    
    **Equipment:**
    - TSSA-approved tanks (double-walled and bench)
    - Fuel pumps and dispensing systems
    - Lubricant equipment (pumps, bench tanks, hose reels)
    
    Contact us at {COMPANY_INFO['phone']} for customized solutions!
    """

def get_credit_application_link() -> str:
    """Get the link to the credit application form."""
    return """
    **Apply for Credit:**
    
    To set up a credit account with Coolman Fuels, please visit:
    👉 https://www.coolmanfuels.ca/credit-application
    
    For questions about credit terms, call us at +1 519-235-0853
    """

def navigate_website(
    page: Annotated[str, "The page to navigate to: 'home', 'commercial', 'residential', 'credit', 'privacy', 'terms'"]
) -> str:
    """Get the URL for a specific page on the Coolman Fuels website."""
    pages = {
        "home": ("Home Page", "https://www.coolmanfuels.ca"),
        "commercial": ("Commercial Solutions", "https://www.coolmanfuels.ca/commercial"),
        "residential": ("Residential Heating", "https://www.coolmanfuels.ca/residential"),
        "credit": ("Credit Application", "https://www.coolmanfuels.ca/credit-application"),
        "privacy": ("Privacy Policy", "https://www.coolmanfuels.ca/terms"),
        "terms": ("Terms and Conditions", "https://www.coolmanfuels.ca/terms-and-conditions")
    }
    
    if page.lower() in pages:
        name, url = pages[page.lower()]
        return f"📄 **{name}:** {url}"
    else:
        return f"Available pages: {', '.join(pages.keys())}"

# ============================================================================
# AGENT SYSTEM INSTRUCTIONS
# ============================================================================

SYSTEM_INSTRUCTIONS = """
You are the friendly and helpful AI assistant for **Coolman Fuels**, a family-owned fuel company 
serving Southwestern Ontario since 1976. Your role is to help customers navigate our website, 
answer questions about our products and services, and provide the best customer experience.

## Your Personality:
- Warm, professional, and helpful
- Knowledgeable about fuel, propane, heating oil, and commercial fuel solutions
- Proactive in suggesting relevant products/services
- Always provide contact information when customers need human assistance

## Key Information:
- Company: Coolman Fuels (formerly Dave Moore Fuels)
- Phone: +1 519-235-0853
- Email: sales@coolmanfuels.ca
- Location: 71321 London Road, Exeter, ON
- Hours: 24/7 availability
- Delivery: Give us a call to set up automatic degree day delivery (it's best to schedule at least one day in advance)

## Service Territory Knowledge:
You have detailed knowledge of our service area covering Huron, Perth, Middlesex, and Lambton 
counties in Southwestern Ontario. Our primary service area extends from:
- NORTH: Goderich and Huron coastline
- EAST: Mitchell and western Perth County
- SOUTH: Grand Bend to Thedford along Lake Huron
- WEST: Forest and Lambton County

When customers ask about service areas, use the check_service_area tool to determine if we serve 
their location. For boundary towns like St. Marys, Stratford, or Ilderton, encourage them to call 
us to confirm - we may be able to serve them! Always be positive and encouraging about serving 
customers. If they're clearly outside our area, direct them to find their nearest Petro-Canada 
marketer at petro-canada.ca/en/business/find-a-marketer. Avoid mentioning non-Petro-Canada 
competitors unless specifically asked.

## Your Capabilities:
1. Answer questions about products (gasoline, diesel, propane, heating oil, lubricants)
2. Explain services (delivery options, cardlock fueling, equipment rentals)
3. Help with residential heating (propane vs heating oil comparisons)
4. Assist commercial customers (fleet cards, bulk fuel, equipment)
5. Check if locations are in our service area (with detailed boundary knowledge)
6. Provide service territory details for commercial customers
7. Provide contact information and website navigation
8. Direct customers to credit applications
9. Explain new customer requirements (tank inspection) and recommend licensed inspectors

## Guidelines:
- Use your tools to provide accurate information
- Be conversational but concise
- If you don't know something, direct customers to call +1 519-235-0853
- Emphasize our key benefits: 24/7 service availability, automatic degree day delivery, Never Run Out Guarantee
- For furnace oil, encourage customers to call us to set up automatic degree day delivery
- For all deliveries, it's best to schedule at least one day in advance. We're here to ensure you never run out of fuel!
- Same-day delivery is only for emergency situations - do not advertise it
- For commercial customers, emphasize our cardlock network and bulk delivery
- **Always reference both Gallons AND Litres** when discussing tank sizes or fuel quantities
- **For gas, diesel, dyed diesel:** Typical tank sizes are 300-500 gallons (1,135-1,890 litres), with 1,000+ gallons for large operations
- **For furnace oil tanks:** Standard is 900L - only mention if customer specifically asks about tank sizes
- **Tank supply by Coolman Fuels:** We can supply a tank if roughly 7,000-8,000 litres per year goes through it. Otherwise, it doesn't make sense for us to supply. If customer wants info on buying their own tank, tell them to call us at +1 519-235-0853
- **For NEW customers** wanting propane, furnace oil, or generator deliveries: they MUST get a tank inspection first. Recommend Avon Heating (519-348-0514) as primary, or Rob Lynn/Town & Country (519-878-0954) as secondary
- **DEF:** Just say we have DEF available. Only mention the brand (Air1 bulk, Catalys jugs) if the customer specifically asks what kind/brand of DEF we carry
"""

# ============================================================================
# MAIN AGENT SETUP
# ============================================================================

async def create_coolman_agent():
    """Create and return the Coolman Fuels AI agent."""
    
    # Get GitHub token from environment variable
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("Please set the GITHUB_TOKEN environment variable with your GitHub Personal Access Token")
    
    # Initialize OpenAI client with GitHub Models endpoint
    openai_client = AsyncOpenAI(
        base_url="https://models.github.ai/inference",
        api_key=github_token,
    )
    
    # Create the chat client
    chat_client = OpenAIChatClient(
        async_client=openai_client,
        model_id="openai/gpt-4.1-mini"  # Free-tier GitHub model, great for customer support
    )
    
    # Create the agent with all tools
    agent = ChatAgent(
        chat_client=chat_client,
        name="Coolman Fuels Assistant",
        instructions=SYSTEM_INSTRUCTIONS,
        tools=[
            get_company_info,
            get_products_list,
            get_services_list,
            get_contact_info,
            check_service_area,
            get_service_area_details,
            get_fleet_card_info,
            get_residential_heating_info,
            get_new_customer_requirements,
            get_commercial_solutions,
            get_credit_application_link,
            navigate_website,
        ],
    )
    
    return agent

async def chat_with_agent():
    """Interactive chat session with the Coolman Fuels agent."""
    print("=" * 60)
    print("🛢️  Welcome to Coolman Fuels Customer Support!")
    print("=" * 60)
    print("I'm here to help you with fuel, propane, heating oil,")
    print("and all our products and services.")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("=" * 60)
    print()
    
    agent = await create_coolman_agent()
    thread = agent.get_new_thread()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print("\nAssistant: Thank you for visiting Coolman Fuels! If you have any")
                print("questions, call us at +1 519-235-0853. Have a great day! 👋")
                break
            
            print("\nAssistant: ", end="", flush=True)
            async for chunk in agent.run_stream(user_input, thread=thread):
                if chunk.text:
                    print(chunk.text, end="", flush=True)
            print("\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! Contact us at +1 519-235-0853 for any questions.")
            break
        except Exception as e:
            print(f"\nSorry, I encountered an error: {e}")
            print("Please try again or call us at +1 519-235-0853 for assistance.\n")

async def demo_responses():
    """Demonstrate the agent with sample customer queries."""
    print("=" * 60)
    print("🛢️  Coolman Fuels Agent Demo")
    print("=" * 60)
    
    agent = await create_coolman_agent()
    thread = agent.get_new_thread()
    
    demo_queries = [
        "What products do you offer?",
        "Do you deliver to Grand Bend?",
        "Tell me about your residential heating options",
        "How can I get a fleet card?",
        "What's your phone number?",
    ]
    
    for query in demo_queries:
        print(f"\n👤 Customer: {query}")
        print("🤖 Assistant: ", end="", flush=True)
        
        async for chunk in agent.run_stream(query, thread=thread):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n" + "-" * 40)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        asyncio.run(demo_responses())
    else:
        asyncio.run(chat_with_agent())
