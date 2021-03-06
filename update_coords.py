#!/usr/bin/env python3

from functions import connect, get_coords_from_address, get_route_length
from time import sleep

def update_gps_routelen():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT rooms.id, address FROM rooms LEFT JOIN rooms_coords ON rooms_coords.room_id = rooms.id WHERE path_len IS NULL AND alive = 1")

    res = cur.fetchall()

    for x in res:
        coords = get_coords_from_address(x[1])

        c = conn.cursor()
        c.execute("SELECT * FROM rooms_coords WHERE room_id = :id", {'id': x[0]})
        r = c.fetchall()

        if coords:
            route_len = get_route_length(coords, [59.947210, 30.255479])
        else:
            print("Skipped", x)
            continue
            # route_len = -1

        print(x, coords, route_len)

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
    sleep(1)


if __name__ == '__main__':
    update_gps_routelen()
