# API Reference

Base URL: `http://127.0.0.1:8372/api`

## Endpoints

### Health Check

```
GET /api/health
```

Returns server status.

**Response:**
```json
{
  "data": {
    "status": "ok",
    "service": "ACE-Step Gradio API",
    "version": "1.0"
  },
  "code": 200
}
```

---

### Generate Music

```
POST /api/release_task
Content-Type: application/json
```

Creates a music generation task.

**Request Body:**
```json
{
  "prompt": "upbeat electronic dance music, 128 BPM",
  "lyrics": "[verse]\nLyrics here...",
  "audio_duration": 30,
  "inference_steps": 8,
  "guidance_scale": 7.0,
  "seed": -1,
  "batch_size": 2
}
```

**Parameters:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `prompt` | string | "" | Music description/caption |
| `lyrics` | string | "" | Song lyrics (optional) |
| `audio_duration` | int | -1 | Duration in seconds (-1 = auto) |
| `bpm` | int | null | Beats per minute |
| `key_scale` | string | "" | Musical key (e.g., "C major") |
| `inference_steps` | int | 8 | Quality vs speed tradeoff |
| `guidance_scale` | float | 7.0 | How closely to follow prompt |
| `seed` | int | -1 | Random seed (-1 = random) |
| `batch_size` | int | 2 | Number of variations |
| `sample_mode` | bool | false | Use LLM to auto-generate content |
| `sample_query` | string | "" | Description for sample_mode |

**Response:**
```json
{
  "data": {
    "task_id": "uuid-here",
    "status": "succeeded"
  },
  "code": 200
}
```

---

### Query Results

```
POST /api/query_result
Content-Type: application/json
```

Get results for completed tasks.

**Request Body:**
```json
{
  "task_id_list": ["uuid-1", "uuid-2"]
}
```

**Response:**
```json
{
  "data": [
    {
      "task_id": "uuid-1",
      "status": 1,
      "result": "[{\"file\": \"/path/to/audio.mp3\", \"url\": \"/api/v1/audio?path=...\"}]"
    }
  ],
  "code": 200
}
```

---

### Download Audio

```
GET /api/v1/audio?path=/path/to/file.mp3
```

Downloads generated audio file.

**Response:** Audio file (audio/mpeg or audio/wav)

---

### Format Input (LLM)

```
POST /api/format_input
Content-Type: application/json
```

Use LLM to enhance prompt/lyrics.

**Request Body:**
```json
{
  "prompt": "rock song",
  "lyrics": "some lyrics",
  "temperature": 0.85
}
```

**Response:**
```json
{
  "data": {
    "caption": "enhanced rock song description...",
    "lyrics": "formatted lyrics...",
    "bpm": 120,
    "key_scale": "E minor",
    "duration": 180
  },
  "code": 200
}
```

---

### Random Sample

```
POST /api/create_random_sample
Content-Type: application/json
```

Get random example parameters from presets.

**Request Body:**
```json
{
  "sample_type": "simple_mode"
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "data": null,
  "code": 500,
  "error": "Error message here"
}
```

Common error codes:
- `400` - Bad request / invalid parameters
- `401` - Unauthorized (if API key required)
- `404` - Resource not found
- `500` - Server error
