#!/usr/bin/env python3

from functions import connect, get_coords_from_address, get_route_length

conn = connect()
cur = conn.cursor()

cur.execute("SELECT id, address FROM rooms")

res = cur.fetchall()

for x in res:
    coords = get_coords_from_address(x[1])

    c = conn.cursor()
    c.execute("SELECT * FROM rooms_coords WHERE room_id = :id", {'id': x[0]})
    r = c.fetchall()

    route_len = get_route_length(coords, [59.947210, 30.255479])

    if r:
        # update
        c.execute("UPDATE rooms_coords SET lat=:lat, lon=:lon, path_len=:len WHERE room_id = :id", {
            'lat': coords[0],
            'lon': coords[0],
            'id': x[0],
            'len': route_len
        })
        conn.commit()
    else:
        # insert
        c.execute("INSERT INTO rooms_coords (room_id, lat, lon, path_len) VALUES (:id, :lat, :lon, :len)", {
            'lat': coords[0],
            'lon': coords[0],
            'id': x[0],
            'len': route_len
        })
        conn.commit()



    # break

