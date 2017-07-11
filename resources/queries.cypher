WITH split(tolower("To Sherlock Holmes she is always the woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler. All emotions, and that one particularly, were abhorrent to his cold, precise but admirably balanced mind. He was, I take it, the most perfect reasoning and observing machine that the world has seen, but as a lover he would have placed himself in a false position. He never spoke of the softer passions, save with a gibe and a sneer. They were admirable things for the observer—excellent for drawing the veil from men’s motives and actions. But for the trained reasoner to admit such intrusions into his own delicate and finely adjusted temperament was to introduce a distracting factor which might throw a doubt upon all his mental results. Grit in a sensitive instrument, or a crack in one of his own high-power lenses, would not be more disturbing than a strong emotion in a nature such as his. And yet there was but one woman to him, and that woman was the late Irene Adler, of dubious and questionable memory."), " ") AS text
UNWIND range(0, size(text)-2) AS i
MERGE (w1:Word {string: text[i]})
    ON CREATE SET w1.count = 1
    ON MATCH SET w1.count = w1.count + 1
MERGE (w2:Word {string: text[i+1]})
    ON CREATE SET w2.count = 1
    ON MATCH SET w2.count = w2.count + 1
MERGE (w1)-[r:NEXT]->(w2)
    ON CREATE SET r.count = 1
    ON MATCH SET r.count = r.count + 1


WITH split(tolower("I had seen little of Holmes lately. My marriage had drifted us away from each other. My own complete happiness, and the home-centred interests which rise up around the man who first finds himself master of his own establishment, were sufficient to absorb all my attention, while Holmes, who loathed every form of society with his whole Bohemian soul, remained in our lodgings in Baker Street, buried among his old books, and alternating from week to week between cocaine and ambition, the drowsiness of the drug, and the fierce energy of his own keen nature. He was still, as ever, deeply attracted by the study of crime, and occupied his immense faculties and extraordinary powers of observation in following out those clues, and clearing up those mysteries which had been abandoned as hopeless by the official police. From time to time I heard some vague account of his doings: of his summons to Odessa in the case of the Trepoff murder, of his clearing up of the singular tragedy of the Atkinson brothers at Trincomalee, and finally of the mission which he had accomplished so delicately and successfully for the reigning family of Holland. Beyond these signs of his activity, however, which I merely shared with all the readers of the daily press, I knew little of my former friend and companion."), " ") AS text
UNWIND range(0, size(text)-2) AS i
MERGE (w1:Word {string: text[i]})
    ON CREATE SET w1.count = 1
    ON MATCH SET w1.count = w1.count + 1
MERGE (w2:Word {string: text[i+1]})
    ON CREATE SET w2.count = 1
    ON MATCH SET w2.count = w2.count + 1
MERGE (w1)-[r:NEXT]->(w2)
    ON CREATE SET r.count = 1
    ON MATCH SET r.count = r.count + 1
    
// Delete all nodes/relations and start again
MATCH (w:Word)
DETACH DELETE w


// Word pairs
MATCH (w1:Word)-[r:NEXT]->(w2:Word)
RETURN [w1.string, w2.string] AS word_pair, r.count AS count
ORDER BY count DESC LIMIT 5

// shortest path
MATCH (w1:Word {string: "holmes"}), (w2:Word {string: "emotion"}),
      path = allShortestPaths((w1)-[:NEXT*]-(w2))
RETURN path


// Words preceding
MATCH (s:Word {word: "holmes"})
MATCH (w:Word)-[:NEXT_WORD]->(s)
RETURN w.word as word

// Words following
MATCH (s:Word {word: "holmes"})
MATCH (w:Word)<-[:NEXT_WORD]-(s)
RETURN w.word as word

// shortest path
MATCH (w1:Word {word: "holmes"}), (w2:Word {word: "adler"}),
      path = allShortestPaths((w1)-[:NEXT_WORD*]-(w2))
RETURN path