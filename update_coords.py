#!/usr/bin/env python3

from functions import connect, get_coords_from_address

conn = connect()
cur = conn.cursor()

cur.execute("SELECT id, address FROM rooms")

res = cur.fetchall()

for x in res:
    print(x)
    coords = get_coords_from_address(x[1])
    print(coords)

    c = conn.cursor()
    c.execute("SELECT * FROM rooms_coords WHERE room_id = :id", {'id': x[0]})
    r = c.fetchall()

    if r:
        # update
        c.execute("UPDATE rooms_coords SET lat=:lat, lon=:lon WHERE room_id = :id", {
            'lat': coords[0],
            'lon': coords[0],
            'id': x[0]
        })
        conn.commit()
    else:
        # insert
        c.execute("INSERT INTO rooms_coords (room_id, lat, lon) VALUES (:id, :lat, :lon)", {
                'lat': coords[0],
                'lon': coords[0],
                'id': x[0]
        })



    break

