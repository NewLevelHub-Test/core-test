"""Seed data: 15 chess topic blocks with lessons and exercises."""
from app import db
from app.models.topic import Topic
from app.models.lesson import Lesson
from app.models.exercise import Exercise

TOPICS_DATA = [
    {
        "name": "Шахматная доска и нотация",
        "description": "Изучение доски, полей, горизонталей, вертикалей и нотации",
        "lessons": [
            {
                "title": "Устройство шахматной доски",
                "content": "Шахматная доска состоит из 64 клеток — 8 горизонталей и 8 вертикалей.",
                "difficulty": "pawn",
                "theory_cards": [
                    {"title": "64 клетки", "text": "Доска имеет 32 белых и 32 чёрных клетки, расположенных в шахматном порядке."},
                    {"title": "Вертикали и горизонтали", "text": "Вертикали обозначаются буквами a-h, горизонтали — цифрами 1-8."},
                    {"title": "Диагонали", "text": "Диагонали соединяют клетки одного цвета по косой линии."},
                ],
                "board_examples": [
                    {"fen": "8/8/8/8/8/8/8/8 w - - 0 1", "description": "Пустая доска для изучения полей"},
                ],
                "exercises": [
                    {"fen": "8/8/8/3Q4/8/8/8/4K3 w - - 0 1", "correct_move": "d4d8", "hint": "Поставьте ферзя на d8", "explanation": "Ферзь перемещается по вертикали d с d4 на d8", "difficulty": "pawn"},
                ],
            },
            {
                "title": "Шахматная нотация",
                "content": "Как записывать и читать ходы в шахматах.",
                "difficulty": "pawn",
                "theory_cards": [
                    {"title": "Алгебраическая нотация", "text": "Каждая клетка имеет уникальный адрес: буква вертикали + цифра горизонтали. Например, e4."},
                    {"title": "Запись ходов", "text": "К = конь, С = слон, Л = ладья, Ф = ферзь, Кр = король. Пешка записывается без буквы."},
                ],
                "board_examples": [
                    {"fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", "description": "Позиция после 1.e4"},
                ],
                "exercises": [
                    {"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "correct_move": "e2e4", "hint": "Самый популярный первый ход — e4", "explanation": "1.e4 — пешка идёт с e2 на e4", "difficulty": "pawn"},
                ],
            },
        ],
    },
    {
        "name": "Как ходят фигуры",
        "description": "Правила ходов каждой фигуры",
        "lessons": [
            {
                "title": "Ладья и слон",
                "content": "Ладья ходит по горизонталям и вертикалям, слон — по диагоналям.",
                "difficulty": "pawn",
                "theory_cards": [
                    {"title": "Ладья", "text": "Ладья перемещается на любое число клеток по горизонтали или вертикали."},
                    {"title": "Слон", "text": "Слон ходит по диагоналям на любое расстояние. У каждого игрока два слона — белопольный и чернопольный."},
                ],
                "board_examples": [
                    {"fen": "8/8/8/8/3R4/8/8/8 w - - 0 1", "description": "Ладья на d4 контролирует вертикаль d и горизонталь 4"},
                ],
                "exercises": [
                    {"fen": "6k1/8/8/8/8/8/3R4/6K1 w - - 0 1", "correct_move": "d2d8", "hint": "Ладья может дать шах на последней горизонтали", "explanation": "Лd8+ — ладья даёт шах по 8-й горизонтали", "difficulty": "pawn"},
                ],
            },
            {
                "title": "Конь и ферзь",
                "content": "Конь прыгает буквой Г, ферзь сочетает силу ладьи и слона.",
                "difficulty": "pawn",
                "theory_cards": [
                    {"title": "Конь", "text": "Конь ходит буквой Г: 2 клетки в одном направлении и 1 в перпендикулярном. Конь может перепрыгивать фигуры."},
                    {"title": "Ферзь", "text": "Ферзь — самая сильная фигура. Он ходит как ладья и слон вместе: по вертикалям, горизонталям и диагоналям."},
                ],
                "board_examples": [
                    {"fen": "8/8/8/8/3N4/8/8/8 w - - 0 1", "description": "Конь на d4 может пойти на 8 полей"},
                ],
                "exercises": [
                    {"fen": "6k1/8/8/3N4/8/8/8/6K1 w - - 0 1", "correct_move": "d5f6", "hint": "Конь может дать шах прыгнув на f6", "explanation": "Кf6+ — шах конём, конь атакует g8 и e8", "difficulty": "pawn"},
                ],
            },
        ],
    },
    {
        "name": "Ценность фигур и размен",
        "description": "Относительная стоимость фигур и выгодные размены",
        "lessons": [
            {
                "title": "Относительная ценность фигур",
                "content": "Пешка = 1, конь = 3, слон = 3, ладья = 5, ферзь = 9.",
                "difficulty": "pawn",
                "theory_cards": [
                    {"title": "Таблица ценности", "text": "Пешка=1, Конь=3, Слон=3, Ладья=5, Ферзь=9. Король бесценен."},
                    {"title": "Когда менять", "text": "Меняйте фигуры, если получаете материальное преимущество. Например, слон за ладью — выгодно для вас."},
                ],
                "board_examples": [
                    {"fen": "r1bqkb1r/pppppppp/2n2n2/8/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3", "description": "Развитие фигур в начале партии"},
                ],
                "exercises": [
                    {"fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", "correct_move": "f3g5", "hint": "Конь атакует слабый пункт f7", "explanation": "Кg5 — нападение на f7, слабый пункт в позиции чёрных", "difficulty": "pawn"},
                ],
            },
        ],
    },
    {
        "name": "Шах и мат",
        "description": "Понятия шаха, мата и пата",
        "lessons": [
            {
                "title": "Шах и способы защиты",
                "content": "Шах — нападение на короля. Три способа защиты: уйти, заслониться, взять атакующую фигуру.",
                "difficulty": "pawn",
                "theory_cards": [
                    {"title": "Что такое шах", "text": "Когда фигура нападает на короля противника — это шах. Король обязан уйти от шаха."},
                    {"title": "Три защиты", "text": "1. Уйти королём. 2. Поставить фигуру между. 3. Взять атакующую фигуру."},
                ],
                "board_examples": [
                    {"fen": "rnb1kbnr/pppppppp/8/8/4q3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1", "description": "Ферзь даёт шах королю на e1"},
                ],
                "exercises": [
                    {"fen": "6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1", "correct_move": "e1e8", "hint": "Ладья может дать мат на последней горизонтали", "explanation": "Ле8# — мат ладьёй на 8-й горизонтали", "difficulty": "pawn"},
                ],
            },
            {
                "title": "Мат в 1 ход",
                "content": "Практика нахождения мата в один ход.",
                "difficulty": "pawn",
                "theory_cards": [
                    {"title": "Что такое мат", "text": "Мат — это шах, от которого нет защиты. Партия заканчивается победой атакующей стороны."},
                    {"title": "Линейный мат", "text": "Две тяжёлые фигуры (ладьи или ферзь+ладья) оттесняют короля к краю и дают мат."},
                ],
                "board_examples": [
                    {"fen": "k7/8/1K6/8/8/8/8/R7 w - - 0 1", "description": "Мат ладьёй: Ла1#"},
                ],
                "exercises": [
                    {"fen": "k7/8/1K6/8/8/8/8/R7 w - - 0 1", "correct_move": "a1a8", "hint": "Ладья даёт мат на последней горизонтали", "explanation": "Ла8# — мат!", "difficulty": "pawn"},
                ],
            },
        ],
    },
    {
        "name": "Рокировка и специальные ходы",
        "description": "Рокировка, взятие на проходе, превращение пешки",
        "lessons": [
            {
                "title": "Рокировка",
                "content": "Рокировка — единственный ход, когда перемещаются две фигуры одновременно.",
                "difficulty": "knight",
                "theory_cards": [
                    {"title": "Короткая рокировка", "text": "Король на g1 (g8), ладья на f1 (f8). Обозначение: O-O."},
                    {"title": "Длинная рокировка", "text": "Король на c1 (c8), ладья на d1 (d8). Обозначение: O-O-O."},
                    {"title": "Условия рокировки", "text": "Король и ладья не ходили, нет шаха, поля между ними не под атакой."},
                ],
                "board_examples": [
                    {"fen": "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1", "description": "Обе стороны могут рокировать"},
                ],
                "exercises": [
                    {"fen": "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1", "correct_move": "e1g1", "hint": "Сделайте короткую рокировку", "explanation": "O-O — король в безопасности за пешками", "difficulty": "knight"},
                ],
            },
        ],
    },
    {
        "name": "Основы дебюта",
        "description": "Принципы начала шахматной партии",
        "lessons": [
            {
                "title": "Три дебютных принципа",
                "content": "Контроль центра, быстрое развитие фигур, безопасность короля.",
                "difficulty": "knight",
                "theory_cards": [
                    {"title": "Контроль центра", "text": "Пешки e4, d4 контролируют центр. Фигуры из центра действуют активнее."},
                    {"title": "Развитие фигур", "text": "Выводите коней и слонов до 5-7 хода. Не ходите одной фигурой дважды без причины."},
                    {"title": "Безопасность короля", "text": "Рокируйте до 10-го хода. Не оставляйте короля в центре."},
                ],
                "board_examples": [
                    {"fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", "description": "Итальянская партия — образцовое развитие"},
                ],
                "exercises": [
                    {"fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", "correct_move": "e7e5", "hint": "Займите центр пешкой", "explanation": "1...e5 — симметричный контроль центра", "difficulty": "knight"},
                ],
            },
            {
                "title": "Типичные ошибки в дебюте",
                "content": "Частые ошибки начинающих и как их избежать.",
                "difficulty": "knight",
                "theory_cards": [
                    {"title": "Ранний выход ферзя", "text": "Не выводите ферзя рано — его будут атаковать, и вы потеряете темпы."},
                    {"title": "Ходы крайними пешками", "text": "Ходы a3, h3 не развивают фигуры. Развивайте коней и слонов."},
                ],
                "board_examples": [
                    {"fen": "rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq g3 0 2", "description": "Плохое начало: f3 и g4 ослабляют короля"},
                ],
                "exercises": [
                    {"fen": "rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq g3 0 2", "correct_move": "d8h4", "hint": "Ферзь может наказать за слабость", "explanation": "Фh4# — мат «Дурака»!", "difficulty": "knight"},
                ],
            },
        ],
    },
    {
        "name": "Тактика: вилка и двойной удар",
        "description": "Нападение одной фигурой на две и более фигур",
        "lessons": [
            {
                "title": "Вилка конём",
                "content": "Конь — лучший мастер вилок, благодаря своему уникальному ходу.",
                "difficulty": "knight",
                "theory_cards": [
                    {"title": "Королевская вилка", "text": "Конь одновременно нападает на короля и ферзя — противник теряет ферзя."},
                    {"title": "Как найти вилку", "text": "Ищите поля, с которых конь атакует сразу две ценные фигуры. Часто это поля c7, f7, e6."},
                ],
                "board_examples": [
                    {"fen": "r1bqk2r/pppp1ppp/2n2n2/4N3/2B1P3/8/PPPP1PPP/RNBQK2R b KQkq - 0 4", "description": "Конь на e5 создаёт угрозы"},
                ],
                "exercises": [
                    {"fen": "r2qk2r/ppp2ppp/8/3N4/8/8/PPP2PPP/R3K2R w KQkq - 0 1", "correct_move": "d5c7", "hint": "Конь может прыгнуть на c7", "explanation": "Кc7+ — вилка на короля и ладью!", "difficulty": "knight"},
                ],
            },
        ],
    },
    {
        "name": "Тактика: связка и открытое нападение",
        "description": "Связки, открытые шахи, рентгеновские атаки",
        "lessons": [
            {
                "title": "Связка",
                "content": "Связка — фигура не может двинуться, т.к. откроет более ценную фигуру.",
                "difficulty": "bishop",
                "theory_cards": [
                    {"title": "Абсолютная связка", "text": "Фигура связана с королём — двигаться нельзя по правилам."},
                    {"title": "Относительная связка", "text": "Фигура связана с более ценной фигурой — двигаться невыгодно."},
                ],
                "board_examples": [
                    {"fen": "rn1qkbnr/ppp1pppp/8/3p4/4P1b1/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3", "description": "Слон g4 связывает коня f3 с ферзём d1"},
                ],
                "exercises": [
                    {"fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3", "correct_move": "f1b5", "hint": "Слон может связать коня c6 с королём", "explanation": "Сb5 — связка коня c6 с королём e8", "difficulty": "bishop"},
                ],
            },
        ],
    },
    {
        "name": "Простые комбинации",
        "description": "Комбинации из 2-3 ходов, жертвы для достижения мата",
        "lessons": [
            {
                "title": "Жертва для мата",
                "content": "Иногда для победы нужно отдать фигуру, чтобы получить мат.",
                "difficulty": "bishop",
                "theory_cards": [
                    {"title": "Отвлечение", "text": "Жертва фигуры, чтобы отвлечь защитника от ключевого поля."},
                    {"title": "Завлечение", "text": "Жертва, которая заставляет фигуру противника встать на неудачное поле."},
                ],
                "board_examples": [
                    {"fen": "r1bqr1k1/pppn1ppp/8/3N4/2BP4/8/PPP2PPP/R2QR1K1 w - - 0 1", "description": "Позиция для комбинации"},
                ],
                "exercises": [
                    {"fen": "6k1/5ppp/8/8/8/2B5/5PPP/6K1 w - - 0 1", "correct_move": "c3f6", "hint": "Слон атакует пешечное прикрытие", "explanation": "Сf6 — угрожает мат на g7", "difficulty": "bishop"},
                ],
            },
        ],
    },
    {
        "name": "Пешечные окончания",
        "description": "Ключевые приёмы пешечных эндшпилей",
        "lessons": [
            {
                "title": "Правило квадрата и оппозиция",
                "content": "Два фундаментальных приёма в пешечных окончаниях.",
                "difficulty": "bishop",
                "theory_cards": [
                    {"title": "Правило квадрата", "text": "Если король попадает в квадрат пешки — он её догонит. Иначе пешка проходит."},
                    {"title": "Оппозиция", "text": "Прямая оппозиция: короли через одну клетку на одной линии. Тот, кто НЕ ходит, владеет оппозицией."},
                ],
                "board_examples": [
                    {"fen": "8/8/8/8/1p6/8/8/1K6 w - - 0 1", "description": "Белый король должен остановить пешку"},
                ],
                "exercises": [
                    {"fen": "8/5k2/8/5K2/5P2/8/8/8 w - - 0 1", "correct_move": "f5e5", "hint": "Займите оппозицию", "explanation": "Крe5 — захватываем оппозицию, пешка проходит", "difficulty": "bishop"},
                ],
            },
        ],
    },
    {
        "name": "Ладейные окончания",
        "description": "Типичные приёмы и позиции ладейных эндшпилей",
        "lessons": [
            {
                "title": "Позиция Лусены и Филидора",
                "content": "Два ключевых теоретических положения в ладейных окончаниях.",
                "difficulty": "rook",
                "theory_cards": [
                    {"title": "Позиция Лусены", "text": "Ладья + пешка + король на 7-й горизонтали. Метод «мостика» для проведения пешки."},
                    {"title": "Позиция Филидора", "text": "Ладья на 6-й горизонтали отрезает короля противника. Ничья при правильной защите."},
                ],
                "board_examples": [
                    {"fen": "1K6/1P1k4/8/8/8/8/2r5/5R2 w - - 0 1", "description": "Позиция Лусены — метод мостика"},
                ],
                "exercises": [
                    {"fen": "1K6/1P1k4/8/8/8/8/2r5/5R2 w - - 0 1", "correct_move": "f1f4", "hint": "Подготовьте мостик ладьёй", "explanation": "Лf4 — начало метода мостика для проведения пешки", "difficulty": "rook"},
                ],
            },
        ],
    },
    {
        "name": "Атака на короля",
        "description": "Принципы и приёмы атаки на короля",
        "lessons": [
            {
                "title": "Типичные жертвы на h7",
                "content": "Классическая жертва слона на h7 — одна из самых частых комбинаций.",
                "difficulty": "rook",
                "theory_cards": [
                    {"title": "Жертва Сxh7+", "text": "Слон бьёт на h7, король вынужден взять, конь прыгает на g5+, далее ферзь на h5 с атакой."},
                    {"title": "Условия для жертвы", "text": "Слон на d3 или c2, конь может прыгнуть на g5, ферзь поддерживает атаку, у чёрных нет Кf6."},
                ],
                "board_examples": [
                    {"fen": "r1bq1rk1/ppp2ppp/2n1pn2/3p4/3P4/3BPN2/PPP2PPP/R1BQ1RK1 w - - 0 7", "description": "Позиция перед жертвой на h7"},
                ],
                "exercises": [
                    {"fen": "r1bq1rk1/ppp2ppp/4pn2/3p2B1/3P4/3BPN2/PPP2PPP/R2Q1RK1 w - - 0 8", "correct_move": "d3h7", "hint": "Классическая жертва слона", "explanation": "Сxh7+! Крxh7 Кg5+ с матовой атакой", "difficulty": "rook"},
                ],
            },
        ],
    },
    {
        "name": "Позиционная игра",
        "description": "Слабые поля, открытые линии, форпосты",
        "lessons": [
            {
                "title": "Слабые поля и форпосты",
                "content": "Слабое поле — клетка, которую нельзя защитить пешкой.",
                "difficulty": "rook",
                "theory_cards": [
                    {"title": "Слабое поле", "text": "Если пешки не могут контролировать клетку — это слабость. Противник может занять её фигурой."},
                    {"title": "Форпост", "text": "Фигура (часто конь) на слабом поле противника, защищённая пешкой — мощный форпост."},
                ],
                "board_examples": [
                    {"fen": "r2q1rk1/pp2ppbp/2np1np1/8/3NP3/2N1BP2/PPPQ2PP/R3KB1R w KQ - 0 9", "description": "Конь d4 — мощный форпост"},
                ],
                "exercises": [
                    {"fen": "r2q1rk1/pp1bppbp/2np1np1/8/3NP3/2N1BP2/PPPQ2PP/R3KB1R w KQ - 0 9", "correct_move": "d4c6", "hint": "Конь может занять слабое поле c6", "explanation": "Кc6 — конь на мощном форпосте, атакует ферзя", "difficulty": "rook"},
                ],
            },
        ],
    },
    {
        "name": "Дебютные системы",
        "description": "Изучение конкретных дебютов",
        "lessons": [
            {
                "title": "Итальянская партия",
                "content": "1.e4 e5 2.Кf3 Кc6 3.Сc4 — один из старейших и надёжных дебютов.",
                "difficulty": "knight",
                "theory_cards": [
                    {"title": "Основная идея", "text": "Белые быстро развивают фигуры и нацеливаются на слабый пункт f7."},
                    {"title": "Гамбит Эванса", "text": "3...Сc5 4.b4!? — жертва пешки за быстрое развитие и инициативу."},
                ],
                "board_examples": [
                    {"fen": "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", "description": "Итальянская партия после 3...Сc5"},
                ],
                "exercises": [
                    {"fen": "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", "correct_move": "c2c3", "hint": "Подготовка пешечного центра d4", "explanation": "c3 — подготавливает d4 с захватом центра", "difficulty": "knight"},
                ],
            },
            {
                "title": "Сицилианская защита",
                "content": "1.e4 c5 — самый популярный ответ на 1.e4.",
                "difficulty": "bishop",
                "theory_cards": [
                    {"title": "Идея чёрных", "text": "Чёрные создают асимметрию и борются за пункт d4. Пешка c5 vs пешка e4."},
                    {"title": "Открытый вариант", "text": "2.Кf3 d6 3.d4 cxd4 4.Кxd4 — самый принципиальный подход."},
                ],
                "board_examples": [
                    {"fen": "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2", "description": "Сицилианская защита после 1...c5"},
                ],
                "exercises": [
                    {"fen": "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2", "correct_move": "g1f3", "hint": "Развитие коня с контролем d4", "explanation": "Кf3 — развитие + подготовка d4", "difficulty": "bishop"},
                ],
            },
        ],
    },
    {
        "name": "Стратегическое планирование",
        "description": "Умение составлять план игры в различных позициях",
        "lessons": [
            {
                "title": "Как составить план",
                "content": "Оценка позиции и выбор плана — ключевой навык шахматиста.",
                "difficulty": "queen",
                "theory_cards": [
                    {"title": "Оценка позиции", "text": "Оцените: материал, безопасность королей, пешечная структура, активность фигур, пространство."},
                    {"title": "Выбор плана", "text": "Найдите слабости противника. Определите, какие фигуры атакуют, какие защищают. Составьте план из 3-5 ходов."},
                    {"title": "Переоценка", "text": "После каждого хода противника пересматривайте план. Гибкость — ключ к успеху."},
                ],
                "board_examples": [
                    {"fen": "r2q1rk1/ppp1bppp/2n1bn2/3pp3/4P3/1BN2N2/PPPP1PPP/R1BQR1K1 w - - 0 8", "description": "Нужно оценить позицию и составить план"},
                ],
                "exercises": [
                    {"fen": "r2q1rk1/ppp1bppp/2n1bn2/3pp3/4P3/1BN2N2/PPPP1PPP/R1BQR1K1 w - - 0 8", "correct_move": "e4d5", "hint": "Вскрытие центра", "explanation": "exd5 — вскрывает линии, активизирует фигуры", "difficulty": "queen"},
                ],
            },
        ],
    },
]


def seed_all_lessons():
    """Insert 15 topic blocks with lessons and exercises."""
    for i, topic_data in enumerate(TOPICS_DATA, start=1):
        existing = Topic.query.filter_by(name=topic_data["name"]).first()
        if existing:
            continue

        topic = Topic(
            name=topic_data["name"],
            description=topic_data["description"],
            order=i,
        )
        db.session.add(topic)
        db.session.flush()

        for j, lesson_data in enumerate(topic_data.get("lessons", []), start=1):
            lesson = Lesson(
                topic_id=topic.id,
                title=lesson_data["title"],
                content=lesson_data.get("content", ""),
                theory_cards=lesson_data.get("theory_cards"),
                board_examples=lesson_data.get("board_examples"),
                difficulty=lesson_data.get("difficulty", "pawn"),
                order=j,
            )
            db.session.add(lesson)
            db.session.flush()

            for k, ex_data in enumerate(lesson_data.get("exercises", []), start=1):
                ex = Exercise(
                    lesson_id=lesson.id,
                    fen=ex_data["fen"],
                    correct_move=ex_data["correct_move"],
                    hint=ex_data.get("hint"),
                    explanation=ex_data.get("explanation"),
                    difficulty=ex_data.get("difficulty", "pawn"),
                    order=k,
                )
                db.session.add(ex)

    db.session.commit()
