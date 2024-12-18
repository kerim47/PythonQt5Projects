import sqlite3
import json

# Test Soruları (Çoktan Seçmeli)
TEST_QUESTIONS = [
    {
        "question": "Python'da Global Interpreter Lock (GIL) neişe yarar?",
        "options": [
            "Hafıza yönetimini kontrol eder",
            "Kodun derlenmesini sağlar",
            "Aynı anda sadece bir thread'in çalışmasını engeller",
            "Performansı artırır",
            "Güvenlik duvarı görevi görür",
        ],
        "correct": "Aynı anda sadece bir thread'in çalışmasını engeller",
    },
    {
        "question": "Descriptor protokolünün temel amacı nedir?",
        "options": [
            "Sınıf metodlarını yönetmek",
            "Öznitelik erişimini ve atamalarını özelleştirmek",
            "Hata yakalamak",
            "Kod optimizasyonu yapmak",
            "Decorator işlevini görmek",
        ],
        "correct": "Öznitelik erişimini ve atamalarını özelleştirmek",
    },
    {
        "question": "Python'da `@staticmethod` decorator'ünün özelliği nedir?",
        "options": [
            "Sınıf örneğine bağımlıdır",
            "İlk parametrede sınıf örneği alır",
            "Sınıf örneği ve sınıftan bağımsızdır",
            "Her çağrımda yeni bir örnek oluşturur",
            "Sadece sınıf metodlarında kullanılabilir",
        ],
        "correct": "Sınıf örneği ve sınıftan bağımsızdır",
    },
    {
        "question": "Metaclass nedir ve neişe yarar?",
        "options": [
            "Sınıfların örnek üretme şeklini değiştirir",
            "Sınıfların kendisini oluşturan sınıftır",
            "Performans optimizasyonu yapar",
            "Hata yakalama mekanizması sağlar",
            "Kod güvenliğini artırır",
        ],
        "correct": "Sınıfların kendisini oluşturan sınıftır",
    },
    {
        "question": "Python'da `*args` ve `**kwargs` kullanımının temel amacı nedir?",
        "options": [
            "Zorunlu parametre tanımlamak",
            "Parametre sayısını sınırlamak",
            "Değişken sayıda ve türde parametre almak",
            "Tip kontrolü yapmak",
            "Performansı artırmak",
        ],
        "correct": "Değişken sayıda ve türde parametre almak",
    },
    {
        "question": "Closure (Kapalı Fonksiyon) konsepti Python'da nasıl çalışır?",
        "options": [
            "Fonksiyonun dış kapsamdaki değişkenlere erişmesini engeller",
            "Fonksiyonun tanımlandığı kapsamdaki değişkenleri hafızada tutar",
            "Sadece global değişkenlere erişim sağlar",
            "Performansı düşürür",
            "Sadece lambda fonksiyonlarında çalışır",
        ],
        "correct": "Fonksiyonun tanımlandığı kapsamdaki değişkenleri hafızada tutar",
    },
    {
        "question": "Generator Expression ile List Comprehension arasındaki temel fark nedir?",
        "options": [
            "Aynı işlevi görürler",
            "Generator daha az bellek tüketir",
            "List Comprehension daha hızlıdır",
            "Generator sadece karmaşık hesaplamalarda kullanılır",
            "List Comprehension daha az bellek tüketir",
        ],
        "correct": "Generator daha az bellek tüketir",
    },
    {
        "question": "Context Manager (`with` ifadesi) hangi amaçla kullanılır?",
        "options": [
            "Performansı artırmak için",
            "Kaynakların otomatik yönetimi için",
            "Hata ayıklama için",
            "Kod güvenliğini sağlamak için",
            "Sadece dosya işlemlerinde kullanılır",
        ],
        "correct": "Kaynakların otomatik yönetimi için",
    },
    {
        "question": "Python'da `__slots__` kullanımının avantajı nedir?",
        "options": [
            "Bellek tüketimini azaltır",
            "Sınıfa dinamik özellik eklemeyi engeller",
            "Performansı artırır",
            "Çoklu kalıtımı destekler",
            "Kod güvenliğini sağlar",
        ],
        "correct": "Bellek tüketimini azaltır",
    },
    {
        "question": "Type Hinting'in temel amacı nedir?",
        "options": [
            "Çalışma zamanı tür kontrolü yapar",
            "Kod okunabilirliğini artırır",
            "Performansı yükseltir",
            "Zorunlu tür dönüşümü sağlar",
            "Hata ayıklamayı kolaylaştırır",
        ],
        "correct": "Kod okunabilirliğini artırır",
    },
    {
        "question": "Python'da Decorator Chaining (Decorator Zincirlemesi) nasıl çalışır?",
        "options": [
            "Decoratorlar sırayla uygulanmaz",
            "Alt decoratordan üst decoratora doğru uygulanır",
            "Üstten alta doğru uygulanır",
            "Sadece bir decorator kullanılabilir",
            "Performansı düşürür",
        ],
        "correct": "Üstten alta doğru uygulanır",
    },
    {
        "question": "Mixin sınıfların kullanım amacı nedir?",
        "options": [
            "Tek bir kalıtım hiyerarşisi oluşturmak",
            "Çoklu kalıtım için kod paylaşımı sağlamak",
            "Sınıf örneği oluşturmak",
            "Hata yakalama mekanizması oluşturmak",
            "Performans optimizasyonu yapmak",
        ],
        "correct": "Çoklu kalıtım için kod paylaşımı sağlamak",
    },
    {
        "question": "`@property` decorator'ünün işlevi nedir?",
        "options": [
            "Sınıf metodlarını gizlemek",
            "Öznitelik erişimini kontrol etmek",
            "Performansı artırmak",
            "Sadece okuma erişimi sağlamak",
            "Kod güvenliğini artırmak",
        ],
        "correct": "Öznitelik erişimini kontrol etmek",
    },
    {
        "question": "Async/Await konseptinin temel amacı nedir?",
        "options": [
            "Çoklu thread oluşturmak",
            "Asenkron programlamayı kolaylaştırmak",
            "Performansı artırmak",
            "Hata yakalama mekanizması oluşturmak",
            "Kod güvenliğini sağlamak",
        ],
        "correct": "Asenkron programlamayı kolaylaştırmak",
    },
    {
        "question": "Python'da `functools.lru_cache()` decorator'ünün işlevi nedir?",
        "options": [
            "Fonksiyon çağrılarını sınırlamak",
            "Fonksiyon sonuçlarını önbelleğe almak",
            "Performansı düşürmek",
            "Hafıza tüketimini artırmak",
            "Hata ayıklamayı kolaylaştırmak",
        ],
        "correct": "Fonksiyon sonuçlarını önbelleğe almak",
    },
    {
        "question": "`__new__` ve `__init__` metodları arasındaki temel fark nedir?",
        "options": [
            "Aynı işlevi görürler",
            "`__new__` sınıf örneği oluşturma, `__init__` başlatma",
            "`__init__` sınıf örneği oluşturma, `__new__` başlatma",
            "Performans farkı vardır",
            "Sadece sınıf metodlarında kullanılır",
        ],
        "correct": "`__new__` sınıf örneği oluşturma, `__init__` başlatma",
    },
    {
        "question": "Python'da Metaclass kullanımının avantajları nelerdir?",
        "options": [
            "Performansı artırmak",
            "Sınıf oluşturma sürecini değiştirmek",
            "Hafıza tüketimini azaltmak",
            "Kod güvenliğini sağlamak",
            "Hata ayıklamayı kolaylaştırmak",
        ],
        "correct": "Sınıf oluşturma sürecini değiştirmek",
    },
    {
        "question": "`__str__` ve `__repr__` metodları arasındaki fark nedir?",
        "options": [
            "Aynı işlevi görürler",
            "`__str__` insan tarafından okunabilir, `__repr__` makine tarafından yorumlanabilir",
            "`__repr__` insan tarafından okunabilir, `__str__` makine tarafından yorumlanabilir",
            "Performans farkı vardır",
            "Sadece hata ayıklamada kullanılır",
        ],
        "correct": "`__str__` insan tarafından okunabilir, `__repr__` makine tarafından yorumlanabilir",
    },
    {
        "question": "Python'da Lazy Evaluation konsepti nasıl çalışır?",
        "options": [
            "Tüm hesaplamaları önceden yapar",
            "Hesaplamaları ihtiyaç anında yapar",
            "Performansı düşürür",
            "Hafıza tüketimini artırır",
            "Sadece generator'larda çalışır",
        ],
        "correct": "Hesaplamaları ihtiyaç anında yapar",
    },
    {
        "question": "`@dataclass` decorator'ünün sağladığı kolaylıklar nelerdir?",
        "options": [
            "Manuel olarak `__init__` tanımlamayı zorlaştırır",
            "Veri sınıfları için otomatik metod üretimi",
            "Performansı düşürür",
            "Sadece sabit sınıflarda çalışır",
            "Kod güvenliğini azaltır",
        ],
        "correct": "Veri sınıfları için otomatik metod üretimi",
    },
]

# Açık Uçlu Sorular
OPEN_QUESTIONS = [
    {
        "question": "Python'da Decorator'ların çalışma mekanizmasını ve kullanım senaryolarını detaylı olarak açıklayınız.",
        "correct": "Decorator'lar, bir fonksiyonun veya sınıfın davranışını değiştirmek veya genişletmek için kullanılan wrapperlardır. Fonksiyonun kaynak kodunu değiştirmeden yeni işlevsellik eklemek mümkündür. Örneğin, bir fonksiyonun çalışma süresini ölçmek, log tutmak, yetkilendirme kontrolü yapmak gibi işlemler decorator'larla kolayca gerçekleştirilebilir. Decorator'lar, başka bir fonksiyonu parametre olarak alan ve orijinal fonksiyonu genişleten yüksek mertebe fonksiyonlardır.",
    },
    {
        "question": "Global Interpreter Lock (GIL)'un Python'daki çok thread'li programlamaya etkilerini ve çözüm yollarını anlatınız.",
        "correct": "GIL, CPython'da aynı anda sadece bir thread'in çalışmasını sağlayan bir mekanizmadır. Bu, çok çekirdekli sistemlerde bile gerçek paralellik elde etmeyi zorlaştırır. CPU-bound görevlerde performansı düşürür. Çözüm yolları şunlardır: 1) Multiprocessing modülü kullanarak gerçek paralellik elde etmek, 2) Asenkron programlama (asyncio) kullanmak, 3) Alternatif Python implementasyonları (Jython, IronPython) kullanmak, 4) NumPy gibi GIL'i atlayan kütüphaneler kullanmak.",
    },
    {
        "question": "Functional Programming konseptlerinin Python'daki uygulamalarını örneklerle açıklayınız.",
        "correct": "Python'da functional programming konseptleri: 1) map(), filter(), reduce() gibi yüksek mertebe fonksiyonlar, 2) Lambda fonksiyonları, 3) List comprehension ve generator expression'lar, 4) Saf fonksiyonlar (yan etki yaratmayan), 5) Immutable veri yapıları kullanımı. Örnek: map() ile liste elemanlarını dönüştürme, filter() ile liste süzme, reduce() ile liste indirgeme, lambda ile kısa fonksiyonlar tanımlama.",
    },
    {
        "question": "Python'da Metaclass kullanımının pratik örneklerini ve avantajlarını detaylandırınız.",
        "correct": "Metaclass, sınıfların nasıl oluşturulduğunu kontrol eden sınıflardır. Kullanım alanları: 1) Otomatik özellik ekleme, 2) Sınıf oluşturma sürecini değiştirme, 3) Kodun yeniden kullanılabilirliğini artırma. Örnek: Tüm sınıflara otomatik log metodu ekleme, sınıf oluşturulurken belirli kısıtlamaları zorlama, abstract base class implementasyonları.",
    },
    {
        "question": "Async/Await konseptini ve asenkron programlamanın Python'daki önemini anlatınız.",
        "correct": "Async/Await, asenkron programlamayı kolaylaştıran Python 3.5+ özellikleridir. I/O bound görevlerde (ağ istekleri, dosya işlemleri) performansı artırır. async def ile asenkron fonksiyon, await ile zaman alan işlemlerin bekletilmesi sağlanır. Tek bir thread içinde birden fazla görevi sırayla çalıştırarak verimlilik sağlar. asyncio kütüphanesi ile network programlama, web scraping gibi alanlarda büyük avantaj sağlar.",
    },
    {
        "question": "Type Hinting ve Type Checking mekanizmalarının Python programlamadaki rolünü ve faydalarını açıklayınız.",
        "correct": "Type Hinting, Python'da değişkenlerin ve fonksiyonların beklenen veri tiplerini belirtmeye olanak sağlar. Faydaları: 1) Kod okunabilirliğini artırır, 2) Statik tip kontrol araçları (mypy) ile hata yakalama, 3) IDE desteği ve otomatik tamamlama, 4) Dokümantasyon görevi görür. Örnek: def topla(x: int, y: int) -> int: return x + y gibi tip açıklamaları kullanılabilir.",
    },
    {
        "question": "Context Manager protokolünün çalışma prensibini ve özel context manager implementasyonlarını örnekleyiniz.",
        "correct": "Context Manager, kaynakların güvenli bir şekilde yönetilmesini sağlayan protokoldür. __enter__() ve __exit__() metodları ile çalışır. Dosya, ağ bağlantıları, veritabanı bağlantıları gibi kaynakların otomatik olarak açılıp kapatılmasını sağlar. Örnek: with open('dosya.txt', 'r') as dosya: işlemler veya @contextmanager decorator kullanarak özel context manager'lar oluşturulabilir.",
    },
    {
        "question": "Python'da Closure ve Decorator ilişkisini ve kullanım senaryolarını detaylı olarak anlatınız.",
        "correct": "Closure, bir fonksiyonun dış kapsamdaki değişkenlere erişebilen iç fonksiyon olmasıdır. Decorator'lar, closure konseptini kullanarak çalışır. Bir fonksiyonu parametre olarak alan ve onu genişleten/değiştiren yüksek mertebe fonksiyonlardır. Örnek kullanımlar: performans ölçümü, yetkilendirme, log tutma, önbellekleme gibi çapraz kesitsel görevler.",
    },
    {
        "question": "Generator ve Iterator konseptlerinin Python'daki uygulamalarını ve performans açısından farklarını açıklayınız.",
        "correct": "Iterator, elemanları sırayla erişilebilen nesnelerdir. __iter__() ve __next__() metodları ile tanımlanır. Generator ise yield anahtar kelimesi ile çalışan, hafızada daha az yer kaplayan iterator'lardır. Performans açısından generator'lar büyük veri setlerinde çok daha verimlidir, çünkü tüm veriyi bir anda bellekte tutmaz, ihtiyaç anında üretir.",
    },
    {
        "question": "Python'da Descriptor protokolünün nesne yönelimli programlamadaki rolünü ve özel descriptor implementasyonlarını örnekleyiniz.",
        "correct": "Descriptor protokolü, bir sınıfın özniteliklerinin nasıl erişileceğini, atanacağını ve silineceğini kontrol eden mekanizmadır. __get__(), __set__() ve __delete__() metodları ile tanımlanır. Özellik kontrolleri, tür dönüşümleri, hesaplanmış özellikler gibi senaryolarda kullanılır. Örnek: property decorator'ü aslında bir descriptor uygulamasıdır.",
    },
]


# Bonus Soruları
BONUS_QUESTION = [
    {
        "question": "0-10 arasındaki çift sayıların karelerini list comprehension ile nasıl elde edersiniz?",
        "correct": "[x**2 for x in range(11) if x % 2 == 0]",
    },
]


class PythonQuizDatabase:
    def __init__(self, db_name="python_quiz.db"):
        """
        Initialize the database connection and create tables
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Create tables for different types of questions
        """
        # Multiple choice questions table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            correct TEXT NOT NULL
        )
        """)

        # Open-ended questions table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS open_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            correct TEXT NOT NULL
        )
        """)

        # Bonus questions table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS bonus_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            correct TEXT NOT NULL
        )
        """)

        self.conn.commit()

    def insert_test_questions(self, questions):
        """
        Insert multiple choice test questions into the database
        """
        for question in questions:
            self.cursor.execute(
                """
            INSERT INTO test_questions (question, options, correct) 
            VALUES (?, ?, ?)
            """,
                (
                    question["question"],
                    json.dumps(question["options"]),
                    question["correct"],
                ),
            )
        self.conn.commit()

    def insert_open_questions(self, questions):
        """
        Insert open-ended questions into the database
        """
        for question in questions:
            self.cursor.execute(
                """
            INSERT INTO open_questions (question, correct) 
            VALUES (?, ?)
            """,
                (question["question"], question["correct"]),
            )
        self.conn.commit()

    def insert_bonus_questions(self, questions):
        """
        Insert bonus questions into the database
        """
        for question in questions:
            self.cursor.execute(
                """
            INSERT INTO bonus_questions (question, correct) 
            VALUES (?, ?)
            """,
                (question["question"], question["correct"]),
            )
        self.conn.commit()

    def get_random_questions(self, table):
        """
        Retrieve random questions from a specified table as a list of dictionaries.
        Each dictionary's keys are the column names, and values are the corresponding column values.
        """
        # Retrieve column names dynamically using PRAGMA table_info to get the column names from the table
        self.cursor.execute(f"PRAGMA table_info({table})")
        columns = [
            column[1] for column in self.cursor.fetchall()
        ]  # Extract column names

        # Now fetch the random rows from the table
        self.cursor.execute(f"""
        SELECT * FROM {table} 
        ORDER BY RANDOM() 
        """)

        # Fetching all rows and formatting them as a list of dictionaries
        rows = self.cursor.fetchall()
        questions_list = []

        for row in rows:
            question_dict = {}
            for i, column in enumerate(columns):
                question_dict[column] = row[
                    i
                ]  # Dynamically adding each column's value to the dictionary

            # Convert the 'options' column (if it exists) from a string representation to an actual list
            if "options" in question_dict:
                question_dict["options"] = eval(question_dict["options"])

            questions_list.append(question_dict)

        return questions_list

    def get_random_questions_back(self, table, limit=1):
        """
        Retrieve random questions from a specified table as a list of dictionaries
        containing 'question', 'options', and 'correct' fields.
        """
        self.cursor.execute(f"""
        SELECT * FROM {table} 
        ORDER BY RANDOM() 
        LIMIT {limit}
        """)

        # Fetching all rows and formatting them as a list of dictionaries
        rows = self.cursor.fetchall()
        questions_list = []

        for row in rows:
            question = row[1]  # Question column (index 1)
            options = eval(
                row[2]
            )  # Converting the string representation of list into an actual list
            correct = row[3]  # Correct answer column (index 3)

            questions_list.append({
                "question": question,
                "options": options,
                "correct": correct,
            })

        return questions_list

    def get_random_questions_org(self, table):
        """
        Retrieve random questions from a specified table
        """
        self.cursor.execute(f"""
        SELECT * FROM {table} 
        ORDER BY RANDOM() 
        """)
        return self.cursor.fetchall()

    def close_connection(self):
        """
        Close the database connection
        """
        self.conn.close()


if __name__ == "__main__":
    db = PythonQuizDatabase()

    # Clear existing data and insert new questions
    db.cursor.execute('DELETE FROM test_questions')
    db.cursor.execute('DELETE FROM open_questions')
    db.cursor.execute('DELETE FROM bonus_questions')

    db.insert_test_questions(TEST_QUESTIONS)
    db.insert_open_questions(OPEN_QUESTIONS)
    db.insert_bonus_questions(BONUS_QUESTION)

    # Example of retrieving random questions
    print("Random Test Questions:")
    test_questions = db.get_random_questions("test_questions")
    print(len(test_questions))

    open_questions = db.get_random_questions("open_questions")
    print(len(open_questions))

    bonus_questions = db.get_random_questions("bonus_questions")
    print(len(bonus_questions))

    db.close_connection()
