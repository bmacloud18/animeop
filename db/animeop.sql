CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    vid_title TEXT NOT NULL,
    vid_url TEXT NOT NULL
);


INSERT INTO videos (vid_title, vid_url) VALUES 
    ('Fairy Tail Opening 1', 'https://www.youtube.com/watch?v=9jvVBVcZ0-Y'), 
    ('Dragon Ball Z Opening', 'https://www.youtube.com/watch?v=R4vjJrGeh1c'),
    ('One Piece Opening 20', 'https://www.youtube.com/watch?v=Oo52vQyAR6w'),
    ('Demon Slayer Opening 1', 'https://www.youtube.com/watch?v=YkJvHe3KK2c'),
    ('Sword Art Online Opening 1', 'https://www.youtube.com/watch?v=1oOBjyOKu2o'),
    ('Tokyo Ghoul Opening 1', 'https://www.youtube.com/watch?v=7aMOurgDB-o'),
    ('Death Note Opening 1', 'https://www.youtube.com/watch?v=kNyR46eHDxE'),
    ('My Hero Academia Opening 1', 'https://www.youtube.com/watch?v=yu0HjPzFYnY'),
    ('Fullmetal Alchemist: Brotherhood Opening 1', 'https://www.youtube.com/watch?v=elyXcwunIYA'),
    ('Attack on Titan Opening 1', 'https://www.youtube.com/watch?v=8OkpRK2_gVs');