import asyncpg
from typing import Optional
from config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT, OWNER_ADMIN

db: Optional[asyncpg.Connection] = None

async def connect_db():
    global db
    db = await asyncpg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
    )

    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            name VARCHAR(255),
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            code VARCHAR(50) UNIQUE,
            name VARCHAR(255),
            author VARCHAR(255),
            price DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    

    # Ensure `author` column exists for older databases where table was created without it
    await db.execute("ALTER TABLE books ADD COLUMN IF NOT EXISTS author VARCHAR(255);")

    await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            total_price DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
            book_code VARCHAR(50) REFERENCES books(code),
            quantity INTEGER DEFAULT 1,
            price NUMERIC(10,2)
        )
    """)

    books = [
        ("python", "Python asoslari", "Guido van Rossum", 10.99),
        ("django", "Django veb birikmalari", "Adrian Holovaty", 12.99),
        ("sql", "SQL ma'lumotlar bazasi", "Chris Fehily", 8.99),
        ("js", "JavaScript dasturlash", "Brendan Eich", 11.99),
        ("html", "HTML va CSS", "Jon Duckett", 7.99),
        ("react", "React JS chiqish", "Dan Abramov", 14.99),
        ("ai", "Sun'iy Intellekt asoslari", "Andrew Ng", 20.99),
        ("node", "Node.js qo'llanmasi", "Kyle Simpson", 13.99),
        ("rust", "Rust dasturlash tili", "Steve Klabnik", 15.99),
        ("go", "Go tili", "Rob Pike", 12.99),
        ("java", "Java asosiy tushunchalar", "Joshua Bloch", 18.99),
        ("cpp", "C++ yuqori darajalishlari", "Bjarne Stroustrup", 22.99),
        ("csharp", "C# qo'llanmasi", "Eric Lippert", 14.99),
        ("kotlin", "Kotlin dasturlash", "Andrey Breslav", 11.99),
        ("swift", "Swift dasturlash", "Chris Lattner", 16.99),
        ("rb", "Ruby va Rails", "David Heinemeier", 13.99),
        ("php", "PHP veb rivojlanishi", "Rasmus Lerdorf", 10.99),
        ("ts", "TypeScript qo'llanmasi", "Anders Hejlsberg", 15.99),
        ("vue", "Vue.js qo'llanmasi", "Evan You", 12.99),
        ("angular", "Angular birikmasini o'qing", "Igor Minar", 16.99),
        ("svelte", "Svelte qo'llanmasi", "Rich Harris", 11.99),
        ("mongo", "MongoDB ma'lumotlar bazasi", "Kirk Pepperdine", 13.99),
        ("postgres", "PostgreSQL yuqori", "Bruce Momjian", 17.99),
        ("mysql", "MySQL ma'lumotlar bazasi", "Paul DuBois", 14.99),
        ("redis", "Redis keshlash", "Salvatore Sanfilippo", 12.99),
        ("docker", "Docker o'rganish", "Bret Fisher", 19.99),
        ("k8s", "Kubernetes qo'llanmasi", "Kelsey Hightower", 21.99),
        ("aws", "AWS bulutli texnologiya", "Adrian Cantrill", 24.99),
        ("azure", "Azure qo'llanmasi", "Yosef Dinerstein", 22.99),
        ("gcp", "Google Cloud platformasi", "John Hanley", 20.99),
        ("git", "Git versiyalash tizimi", "Jason McCreight", 10.99),
        ("linux", "Linux buyruq satrari", "William Shotts", 9.99),
        ("devops", "DevOps qo'llanmasi", "Gene Kim", 23.99),
        ("ci_cd", "CI/CD qo'llanmasi", "Jeppe Neimand", 16.99),
        ("agile", "Agile metodologiyasi", "Jeff Sutherland", 14.99),
        ("scrum", "Scrum qo'llanmasi", "Ken Schwaber", 11.99),
        ("ml", "Mashina o'rganish", "Andrew Ng", 25.99),
        ("dl", "Chuqur o'rganish", "Ian Goodfellow", 28.99),
        ("nlp", "Tabiiy til qayta ishlash", "Jacob Eisenstein", 26.99),
        ("cv", "Kompyuter ko'rish", "Richard Szeliski", 24.99),
        ("datasc", "Ma'lumotlar tahlili", "Joel Grus", 20.99),
        ("analytics", "Analitika qo'llanmasi", "Avinash Kaushik", 15.99),
        ("bi", "Biznes intellekti", "Kimball Ralph", 21.99),
        ("excel", "Excel o'rganish", "Bill Jelen", 8.99),
        ("power_query", "Power Query qo'llanmasi", "Chris Webb", 12.99),
        ("sap", "SAP tizimi", "Andrew Okungbowa", 24.99),
        ("salesforce", "Salesforce platformasi", "Paul Goodey", 19.99),
        ("erp", "ERP tizimlar", "Marilyn Pratt", 22.99),
        ("crm", "CRM strategiyasi", "Paul Greenberg", 16.99),
        ("marketing", "Raqamli marketing", "Neil Patel", 13.99),
        ("seo", "SEO o'rganish", "Bruce Clay", 11.99),
        ("social", "Ijtimoiy media", "Buffer Team", 9.99),
        ("email", "Email marketing", "Ryan Deiss", 10.99),
        ("content", "Kontent marketingi", "Ann Handley", 12.99),
        ("growth", "O'sish xakkerlik", "Sean Ellis", 14.99),
        ("lean", "Lean startup", "Eric Ries", 11.99),
        ("startup", "Startup qo'llanmasi", "Steve Blank", 13.99),
        ("biz", "Biznes strategiyasi", "Michael Porter", 18.99),
        ("finance", "Moliya qo'llanmasi", "Benjamin Graham", 15.99),
        ("invest", "Investitsiya qo'llanmasi", "Warren Buffett", 17.99),
        ("trade", "Savdo qo'llanmasi", "Alexander Elder", 16.99),
        ("crypto", "Kriptovalyutalar", "Andreas Antonopoulos", 19.99),
        ("blockchain", "Blokchejn texnologiyasi", "Don Tapscott", 17.99),
        ("web3", "Web3 qo'llanmasi", "Gavin Wood", 18.99),
        ("nft", "NFT qo'llanmasi", "Kasper Szymanski", 13.99),
        ("iot", "IoT qo'llanmasi", "Olivier Blanchard", 15.99),
        ("ar_vr", "AR/VR texnologiyalari", "Jeannie Novak", 20.99),
        ("ai_ethics", "AI etika", "Safiya Noble", 16.99),
        ("privacy", "Xususiy hayotning himoyasi", "Bruce Schneier", 14.99),
        ("security", "Kiberxavfsizlik", "Bruce Schneier", 19.99),
        ("hacking", "Xaker qo'llanmasi", "Kevin Mitnick", 18.99),
        ("pentest", "Penetratsion testlash", "Georgia Weidman", 21.99),
        ("forensics", "Raqamli kesgutshunoslim", "Jonathan Beaty", 22.99),
        ("malware", "Zararli dastur tahlili", "Michael Sikorski", 24.99),
        ("reverse", "Teskari injenirlik", "Bruce Dang", 23.99),
        ("exploit", "Exploit rivojlanishi", "Saumil Shah", 25.99),
        ("wireless", "Noto'g'ri yorug'lik xavfsizligi", "Joshua Wright", 17.99),
        ("network", "Tarmoq qo'llanmasi", "Andrew Tanenbaum", 19.99),
        ("tcp_ip", "TCP/IP qo'llanmasi", "Charles Kozierok", 21.99),
        ("routing", "Marshrutlash qo'llanmasi", "Jeff Doyle", 20.99),
        ("switch", "Kommutatsiya qo'llanmasi", "Richard Graziani", 20.99),
        ("dns", "DNS qo'llanmasi", "Cricket Liu", 12.99),
        ("dhcp", "DHCP qo'llanmasi", "Ralph Droms", 11.99),
        ("vpn", "VPN qo'llanmasi", "Cliff Zou", 13.99),
        ("firewall", "Faiyrvoll qo'llanmasi", "Wes Noonan", 14.99),
        ("load_balancer", "Yük balansemachi", "Niels Provos", 15.99),
        ("cache", "Kesh qo'llanmasi", "Phil Karlton", 10.99),
        ("cdn", "CDN qo'llanmasi", "Mark Nottingham", 12.99),
        ("performance", "Ishlashviy ko'rsatkich", "Steve Souders", 14.99),
        ("scaling", "Masshtablash qo'llanmasi", "Nathan Marz", 16.99),
        ("distributed", "Tarqatilgan tizimlar", "Andrew Tanenbaum", 22.99),
        ("consensus", "Konsensus algoritmsi", "Leslie Lamport", 19.99),
        ("testing", "Test qo'llanmasi", "Kent Beck", 13.99),
        ("unit_test", "Birlik testi", "Roy Osherove", 12.99),
        ("integration", "Integral test", "Brian Marick", 11.99),
        ("bdd", "BDD qo'llanmasi", "Dan North", 10.99),
        ("tdd", "TDD qo'llanmasi", "Kent Beck", 11.99),
        ("refactoring", "Qayta tayyorlash", "Martin Fowler", 14.99),
        ("clean_code", "Toza kod yozish", "Robert Martin", 13.99),
        ("design_patterns", "Dizayn shablonlari", "Gang of Four", 16.99),
        ("architecture", "Arxitektura qo'llanmasi", "Sam Newman", 17.99),
        ("microservices", "Mikro-xizmatlar", "Sam Newman", 18.99),
        ("monolith", "Monolitik arxitektura", "Martin Fowler", 12.99),
        ("api", "API dizayn", "Virgil Marianescu", 11.99),
        ("rest", "REST API", "Leonard Richardson", 12.99),
        ("graphql", "GraphQL qo'llanmasi", "Eve Porcello", 13.99),
        ("grpc", "gRPC qo'llanmasi", "Kasun Indrasiri", 14.99),
        ("soap", "SOAP qo'llanmasi", "Don Box", 10.99),
        ("oauth", "OAuth qo'llanmasi", "David Burchell", 11.99),
        ("saml", "SAML qo'llanmasi", "Scott Cantor", 11.99),
        ("jwt", "JWT qo'llanmasi", "Auth0 Team", 9.99),
        ("tls", "TLS qo'llanmasi", "Eric Rescorla", 15.99),
        ("pki", "PKI qo'llanmasi", "Carl Ellison", 13.99),
        ("iam", "IAM qo'llanmasi", "Peter Torr", 14.99),
        ("rbac", "RBAC qo'llanmasi", "David Ferraiolo", 12.99),
        ("abac", "ABAC qo'llanmasi", "David Ferraiolo", 12.99),
        ("logging", "Jurnal qo'llanmasi", "Ceki Gülcü", 9.99),
        ("monitoring", "Monitorlash qo'llanmasi", "Etsy Team", 12.99),
        ("alerting", "Ogohlantirish tizimi", "Bosun Team", 10.99),
        ("tracing", "Tarqatilgan izlash", "Yuri Shkuro", 13.99),
        ("metrics", "Metrik o'lchovlar", "Tom Wilkie", 11.99),
        ("observability", "Kuzatuvchanligi", "Liz Fong-Jones", 14.99),
        ("cost_optimization", "Xarajatlarni optimallashtirish", "AWS Team", 11.99),
        ("sustainability", "Barqarorlik IT", "Jennifer Cobbe", 12.99),
        ("ux_design", "UX dizayn", "Don Norman", 14.99),
        ("ui_design", "UI dizayn", "Ellen Lupton", 13.99),
        ("typography", "Tipografiya qo'llanmasi", "Ellen Lupton", 11.99),
        ("color", "Rang nazariyasi", "Johannes Itten", 12.99),
        ("layout", "Layout dizayni", "Ellen Lupton", 10.99),
        ("design_systems", "Dizayn tizimlar", "Alla Kholmatova", 13.99),
        ("accessibility", "Mumkin bo'lgan kirish", "Gez Lemon", 12.99),
        ("mobile_design", "Mobil dizayn", "Lyndon Cerejo", 11.99),
        ("responsive", "Javob beruvchi dizayn", "Ethan Marcotte", 10.99),
        ("animation", "Animatsiya qo'llanmasi", "Val Head", 12.99),
        ("interaction", "Oʻzaro taʼsir dizayni", "Bill Moggridge", 13.99),
        ("game_design", "O'yin dizayni", "Richard Rouse", 14.99),
        ("game_dev", "O'yin rivojlanishi", "Jason Gregory", 16.99),
        ("unreal", "Unreal Engine", "Ben Tristem", 17.99),
        ("unity", "Unity qo'llanmasi", "Jonathan Linietsky", 15.99),
        ("godot", "Godot Engine", "Juan Linietsky", 12.99),
        ("voxel", "Voksel qo'llanmasi", "Notch", 11.99),
        ("shader", "Shader qo'llanmasi", "Inigo Quilez", 13.99),
        ("graphics", "Grafika qo'llanmasi", "OpenGL Team", 14.99),
        ("physics", "Fizika dviguni", "Erin Catto", 12.99),
        ("audio", "Audio dasturlash", "David Rabinowitz", 11.99),
        ("3d", "3D modellashtirish", "Leigh Whiteaker", 13.99),
        ("blender", "Blender qo'llanmasi", "Blender jamoasi", 14.99),
        ("maya", "Maya qo'llanmasi", "Autodesk", 16.99),
        ("cinema4d", "Cinema 4D", "Maxon", 15.99),
        ("vfx", "VFX qo'llanmasi", "Steve Wright", 16.99),
        ("motion", "Harakatli grafika", "Eran Stern", 13.99),
        ("after_effects", "After Effects", "Trish Meyer", 12.99),
        ("premiere", "Premiere Pro", "Maxim Jago", 11.99),
        ("davinci", "DaVinci Resolve", "BMD", 10.99),
        ("ffmpeg", "FFmpeg qo'llanmasi", "FFmpeg Team", 9.99),
        ("streaming", "Oqim qo'llanmasi", "Wowza Team", 13.99),
        ("broadcast", "Radiofication", "EBU", 14.99),
        ("podcast", "Podcast qo'llanmasi", "Pat Flynn", 8.99),
        ("audio_editing", "Audio tahrirlash", "Bruce Bartlett", 9.99),
        ("music_production", "Musiqa ishlab chiqish", "Ian Shepherd", 12.99),
        ("daw", "DAW qo'llanmasi", "Starkey Hutchins", 11.99),
        ("fl_studio", "FL Studio", "Image-Line", 10.99),
        ("ableton", "Ableton Live", "REZA Tezer", 11.99),
        ("logic", "Logic Pro", "David Dvorin", 12.99),
        ("midi", "MIDI qo'llanmasi", "Craig Sapp", 8.99),
        ("synthesis", "Sintez qo'llanmasi", "Simon Cann", 10.99),
        ("sound_design", "Ovoz dizayni", "Mike Cohen", 11.99),
        ("acoustics", "Akustika qo'llanmasi", "Heinrich Kuttruff", 14.99),
        ("mixing", "Aralashtirish qo'llanmasi", "Bobby Owinski", 12.99),
        ("mastering", "Mastering qo'llanmasi", "Ian Shepherd", 13.99),
        ("vinyl", "Vinil qo'llanmasi", "Mark Isham", 11.99),
        ("hi_fi", "Hi-Fi qo'llanmasi", "Alvin Gold", 13.99),
        ("speaker", "Spiker dizayni", "Vance Dickason", 14.99),
        ("amplifier", "Amplifikator dizayni", "Ray Miller", 15.99),
        ("preamp", "Preamp qo'llanmasi", "John Broskie", 12.99),
        ("headphone", "Quloqlik qo'llanmasi", "Crinacle", 10.99),
        ("microphone", "Mikrofon qo'llanmasi", "Bruce Bartlett", 11.99),
        ("studio", "Studio sozlamasi", "Philip Newell", 13.99),
        ("recording", "Yozuvni qo'llanmasi", "Paul White", 12.99),
        ("live_sound", "Jonli ovoz qo'llanmasi", "Daniel Benton", 11.99),
        ("pa_system", "PA tizimi", "Bob McCarthy", 13.99),
        ("concert", "Kontsert ishlab chiqish", "Janet Reddington", 12.99),
        ("event", "Tadbirni rejalashtirish", "Susan Friedman", 10.99),
        ("wedding", "Turmushga chiqish rejasi", "Preston Bailey", 9.99),
        ("party", "Ziyofatni rejalashtirish", "Mindy Weiss", 8.99),
        ("catering", "Taom tayyorlash", "Marion Cunningham", 10.99),
        ("cooking", "Pishirish qo'llanmasi", "Julia Child", 11.99),
        ("baking", "Pechka qo'llanmasi", "Jacques Torres", 10.99),
        ("pastry", "Pechenye qo'llanmasi", "Jacques Torres", 11.99),
        ("chocolate", "Shokolad tayyorlash", "Jacques Torres", 10.99),
        ("cocktail", "Koktel qo'llanmasi", "Dale DeGroff", 11.99),
        ("coffee", "Qahva qo'llanmasi", "Scott Rao", 9.99),
        ("tea", "Choy qo'llanmasi", "Mary Lou Heiss", 8.99),
        ("wine", "Vino qo'llanmasi", "Karen MacNeil", 12.99),
        ("beer", "Pivo qo'llanmasi", "Randy Mosher", 10.99),
        ("whiskey", "Viskey qo'llanmasi", "Charles MacLean", 11.99),
        ("nutrition", "Ovqatlanish qo'llanmasi", "Walter Willett", 13.99),
        ("diet", "Dieta qo'llanmasi", "Gary Taubes", 12.99),
        ("fitness", "Fitnes qo'llanmasi", "Lyle McDonald", 11.99),
        ("gym", "Shakl qo'llanmasi", "Stan Efferding", 10.99),
        ("yoga", "Yoga qo'llanmasi", "B.K.S. Iyengar", 10.99),
        ("meditation", "Meditatsiya qo'llanmasi", "Jon Kabat-Zinn", 11.99),
        ("mindfulness", "Sog'inchlilik", "Thich Nhat Hanh", 9.99),
        ("psychology", "Psixologiya qo'llanmasi", "Carl Jung", 12.99),
        ("neuroscience", "Neyron fanları", "Eric Kandel", 14.99),
        ("brain", "Miya fanları", "John Ratey", 12.99),
        ("memory", "Xotira qo'llanmasi", "Joshua Foer", 11.99),
        ("learning", "O'rganish fanları", "Barbara Oakley", 12.99),
        ("education", "Ta'lim qo'llanmasi", "bell hooks", 10.99),
        ("teaching", "O'qitish qo'llanmasi", "Paolo Freire", 11.99),
        ("communication", "Muloqot", "Deborah Tannen", 10.99),
        ("presentation", "Taqdimot qo'llanmasi", "Nancy Duarte", 11.99),
        ("public_speaking", "Ommaviy so'zlash", "Dale Carnegie", 9.99),
        ("leadership", "Liderlik qo'llanmasi", "James Kouzes", 12.99),
        ("management", "Menejment qo'llanmasi", "Peter Drucker", 13.99),
        ("hr", "Insan resurslari", "Dave Ulrich", 12.99),
        ("recruitment", "Kadrlarni qabul qilish", "LinkedIn", 10.99),
        ("onboarding", "Onboarding qo'llanmasi", "Talya Bauer", 9.99),
        ("coaching", "Coaching qo'llanmasi", "John Whitmore", 11.99),
        ("mentoring", "Mentoring qo'llanmasi", "Lois Zachary", 10.99),
        ("teamwork", "Jamaviy ish", "Jon Katzenbach", 11.99),
        ("culture", "Kompaniya madaniyati", "Patty McCord", 12.99),
        ("innovation", "Innovatsiya qo'llanmasi", "Clayton Christensen", 13.99),
        ("creativity", "Ijodiy qo'llanmasi", "David Kelley", 12.99),
        ("problem_solving", "Masalani hal qilish", "Charles Kepner", 11.99),
        ("decision", "Qarar qabul qilish", "Daniel Kahneman", 13.99),
        ("logic", "Mantiq qo'llanmasi", "Aristotle", 10.99),
        ("philosophy", "Falsafa qo'llanmasi", "Ludwig Wittgenstein", 11.99),
        ("ethics", "Etika qo'llanmasi", "Peter Singer", 12.99),
        ("morality", "Axloq qo'llanmasi", "Jonathan Haidt", 12.99),
        ("justice", "Adolat qo'llanmasi", "John Rawls", 13.99),
        ("law", "Qonun qo'llanmasi", "Oliver Wendell Holmes", 12.99),
        ("constitutional", "Konstitutsion huquq", "Laurence Tribe", 14.99),
        ("criminal", "Ijrimiy huquq", "Paul Robinson", 13.99),
        ("civil", "Fuqaro huquqi", "John Calamari", 12.99),
        ("contract", "Shartnoma huquqi", "E. Allan Farnsworth", 13.99),
        ("patent", "Patent huquqi", "William Cornish", 14.99),
        ("copyright", "Mualliflik huquqi", "David Nimmer", 13.99),
        ("trademark", "Savdo belgisi", "J. Gilson", 12.99),
        ("ip", "IP qo'llanmasi", "Paul Goldstein", 13.99),
    ]


    for b in books:
        await db.execute(
            "INSERT INTO books (code, name, author, price) VALUES ($1,$2,$3,$4) ON CONFLICT (code) DO NOTHING",
            *b
        )

    print("✅ DB tayyor")

async def check_admin(user_id: int):
    if user_id == OWNER_ADMIN:
        return True
    return await db.fetchval(
        "SELECT is_admin FROM users WHERE telegram_id=$1",
        user_id
    ) or False

# ---------------- DB helper functions ----------------
async def get_book_by_code(code: str):
    return await db.fetchrow("SELECT code,name,author,price FROM books WHERE code=$1", code)

async def get_books_by_codes(codes: list):
    if not codes:
        return []
    return await db.fetch("SELECT code,name,author,price FROM books WHERE code = ANY($1::text[])", codes)

async def create_order(user_id: int, total_price: float, items: list | None = None):
    """Create an order and optionally save selected book items.

    - `items` should be a list of book `code` strings. Each item will be
      inserted into `order_items` with quantity=1 and the current book price.
    Returns the new order id.
    """
    async with db.transaction():
        order_id = await db.fetchval(
            "INSERT INTO orders (user_id, total_price) VALUES ($1,$2) RETURNING id",
            user_id, total_price
        )

        if items:
            for code in items:
                book = await db.fetchrow("SELECT price FROM books WHERE code=$1", code)
                price = float(book['price']) if book else 0.0
                await db.execute(
                    "INSERT INTO order_items (order_id, book_code, quantity, price) VALUES ($1,$2,$3,$4)",
                    order_id, code, 1, price
                )

    return order_id

async def delete_book(code: str):
    await db.execute("DELETE FROM books WHERE code=$1", code)

async def search_books(query: str):
    return await db.fetch(
        "SELECT code,name,author,price FROM books WHERE name ILIKE $1 OR author ILIKE $1 ORDER BY created_at DESC",
        f"%{query}%"
    )

async def close_db():
    global db
    if db is not None:
        await db.close()
        db = None
        print("✅ DB closed")



