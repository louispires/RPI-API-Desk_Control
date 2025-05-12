# RPI-API-Desk_Control
# Desk Control API - Usage Guide

This guide describes how to interact with the Raspberry Pi Desk Control API using HTTP requests.

## Base URL

```
http://<raspberry_pi_ip>
```

Replace `<raspberry_pi_ip>` with the actual IP address of your Pi on the network.

---

## Endpoints

### 1. Get Current Height

```
GET /
```

* Returns the current desk height.
* Response: rendered HTML with height value.

### 2. Move Desk Up or Down (to preset position)

```
POST /UP
POST /DOWN
```

* Moves desk to preset UP or DOWN position.
* Response: "Desk is going UP" / "Desk is going DOWN"

### 3. Micro Move and Hold

```
POST /UP/micro
POST /DOWN/micro
```

* Starts micro-move in the specified direction.
* Relay stays ON until `POST /stop` is called.
* Response: "Desk is holding micro-move UP"

### 4. Stop Movement

```
POST /stop
```

* Stops current movement and turns off relay.
* Response: "Desk has been stopped!"

### 5. Set Current Height as Preset

```
POST /set/UP
POST /set/DOWN
```

* Saves the current height as the new UP or DOWN preset.
* Response: "Desk UP position set to 102.3"

### 6. Read Preset Height

```
GET /read/UP
GET /read/DOWN
```

* Returns stored height value for UP or DOWN.

### 7. Adjust Height by Delta (cm)

```
POST /UP/<delta>
POST /DOWN/<delta>
```

Example:

```
POST /UP/2.5
```

* Has to be decimal value: 2.0
* Moves the desk up by 2.5 cm from current height.
* Response: "Desk is adjusting height UP by 2.5 cm"

---

## Example Using curl

```
curl -X POST http://192.168.1.42/UP/micro
sleep 2
curl -X POST http://192.168.1.42/stop
```

---

## Notes

* All move endpoints are asynchronous (they spawn background threads).
* Only one motion command should run at a time.
* Micro move holds the relay ON until stopped.
