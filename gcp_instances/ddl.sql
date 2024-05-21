CREATE OR REPLACE TABLE music_core.auth_events (
  sk string,
  artist string,
  state string,
  city string,
  registration_ts timestamp
) PARTITION BY TIMESTAMP_TRUNC(registration_ts, DAY);

CREATE OR REPLACE TABLE music_core.listen_events (
  sk string,
  event_ts timestamp,
  artist string,
  song string,
  listen_duration int,
  song_duration int,
  state string,
  city string,
  username string,
  user_gender string,
  user_type string
 ) PARTITION BY TIMESTAMP_TRUNC(event_ts, DAY);

 CREATE OR REPLACE TABLE music_core.page_view_events(
    sk string,
    event_ts timestamp,
    page string,
    duration int,
    artist string,
    state string,
    city string,
    user_gender string,
    user_type string,
    username string
 ) PARTITION BY TIMESTAMP_TRUNC(event_ts, DAY);

CREATE OR REPLACE VIEW music_dm.v_users AS (
  SELECT 
  CAST(event_ts AS DATE) as t_date,
  user_gender as gender,
  user_type as type, 
  COUNT(DISTINCT username) AS amount, 
  FROM music_core.listen_events
  GROUP BY CAST(event_ts AS DATE), user_gender, user_type
);

CREATE OR REPLACE VIEW music_dm.v_top_songs AS (
  SELECT 
  CAST(event_ts AS DATE) as t_date,
  song as song,
  COUNT(sk) as streams
  FROM music_core.listen_events
  WHERE listen_duration / song_duration > 0.3
  GROUP BY CAST(event_ts AS DATE), artist, song
);

CREATE OR REPLACE VIEW music_dm.v_top_artists AS (
  SELECT 
  CAST(event_ts AS DATE) as t_date,
  artist as artist,
  COUNT(sk) as streams
  FROM music_core.listen_events
  WHERE listen_duration / song_duration > 0.3
  GROUP BY CAST(event_ts AS DATE), artist
  LIMIT 10
);

CREATE OR REPLACE VIEW music_dm.v_state_activeness AS (
  SELECT
  CAST(event_ts AS DATE) as t_date,
  CONCAT('US-', state) as state_code,
  COUNT(sk) as streams
  FROM music_core.listen_events
  WHERE listen_duration / song_duration > 0.3
  GROUP BY CAST(event_ts AS DATE), CONCAT('US-', state)
);

CREATE OR REPLACE VIEW music_dm.v_streams_permutation AS (
  SELECT 
  CAST(event_ts AS DATE) as t_date,
  CAST(TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), HOUR) as TIME) AS t_time,
  COUNT(sk) as streams
  FROM music_core.listen_events
  WHERE listen_duration / song_duration > 0.3
  GROUP BY CAST(event_ts AS DATE), CAST(TIMESTAMP_TRUNC(event_ts, HOUR) as TIME)
  );
