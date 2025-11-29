# 🐛 Supabase PostgreSQL Connection Issue on Windows — Root Cause & Fix

## 📌 Overview

When connecting to a Supabase PostgreSQL database using `psycopg3` on a Windows machine, the connection may fail even though the exact same code works on Google Colab and TCP connectivity to port 6543 is verified as working.

### Typical Error Message

```
OperationalError: connection to server at "13.200.110.68" failed:
server closed the connection unexpectedly
This probably means the server terminated abnormally before or while processing the request.
```

### Symptoms

This issue persists even when:

- ✅ Using a mobile hotspot
- ✅ Reinstalling `psycopg`
- ✅ Verifying Windows firewall isn't blocking connections
- ✅ Checking that the port is open (`Test-NetConnection` succeeds)
- ✅ Confirming the date/time are correct
- ✅ Ensuring no antivirus is installed

### The Quick Fix

The connection works instantly after adding:

```python
gssencmode=disable
```

to the connection parameters.

---

## ✅ Root Cause

### 🔍 GSSAPI Encryption Negotiation Failure

The Windows environment runs a `psycopg` build linked with `libpq` that supports GSSAPI encryption (`gssenc`).

**Default behavior for such builds:**

1. Try GSS encryption first
2. Then fall back to SSL/TLS

**What happens with Supabase:**

Supabase's pooled PostgreSQL endpoint **does not support GSSAPI encryption negotiation**, so when the Windows client attempts a GSS handshake:

1. ✅ TCP connection succeeds
2. 🔄 libpq initiates GSSAPI negotiation
3. ❌ Supabase immediately closes the socket
4. ⚠️ psycopg reports: `server closed the connection unexpectedly`

### Why Google Colab Works

Google Colab works because its `psycopg` installation is built **without GSS support**, so it goes directly to SSL, avoiding this failure entirely.

---

## ✅ The Solution

Explicitly disable GSSAPI encryption and force `libpq` to use only SSL/TLS.

### ✔ Working Python Code

#### Option 1: Connection String with Parameters

```python
import psycopg

conn = psycopg.connect(
    "postgresql://postgres.fzdaenmsnnkewcmphzhu:5sZMOh1Q8Q5V3sK5"
    "@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
    "?sslmode=require&gssencmode=disable",
    connect_timeout=10,
)

print("✅ Connected successfully!")
conn.close()
```

#### Option 2: Using Keyword Arguments

```python
import psycopg

conn = psycopg.connect(
    host="aws-1-ap-south-1.pooler.supabase.com",
    port=6543,
    dbname="postgres",
    user="postgres.fzdaenmsnnkewcmphzhu",
    password="5sZMOh1Q8Q5V3sK5",
    sslmode="require",
    gssencmode="disable",  # ⭐ Critical for Windows
    connect_timeout=10,
)

print("✅ Connected successfully!")
conn.close()
```

### 🧠 Why This Fix Works

Setting `gssencmode=disable` forces `libpq` to:

- ❌ Skip GSSAPI encryption completely
- ✅ Use only SSL/TLS
- ✔️ Avoid the negotiation step that Supabase rejects

This aligns the Windows client's behavior with Colab's `psycopg` build, making the connection succeed.

---

## 📌 Recommendation for All Cloud PostgreSQL Environments

Most cloud providers do **not** support or expect GSSAPI encryption:

- Supabase
- Neon
- Render
- AWS RDS
- Railway
- DigitalOcean Managed Databases

### Best Practice

To ensure portability across machines and operating systems:

**Always add `gssencmode=disable` to your PostgreSQL connection strings when using `psycopg` on Windows.**

### Example for Environment Variables

```python
import os
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure gssencmode is disabled
if "gssencmode" not in DATABASE_URL:
    separator = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{separator}gssencmode=disable"

conn = psycopg.connect(DATABASE_URL)
```

---

## 🎉 Final Notes

This issue is **subtle** because:

- ✅ Port tests pass
- ✅ DNS resolution works
- ✅ SSL certificates are valid
- ✅ Supabase infrastructure is healthy
- ❌ Error message is ambiguous

**The problem lies entirely in a `libpq` feature mismatch**, not in:

- Supabase configuration
- Python installation
- Network connectivity
- Firewall settings

---

## 📚 Additional Resources

### Connection String Parameters

| Parameter           | Description                   | Recommended Value                 |
| ------------------- | ----------------------------- | --------------------------------- |
| `sslmode`         | SSL/TLS encryption mode       | `require` or `verify-full`    |
| `gssencmode`      | GSSAPI encryption mode        | `disable` (for cloud providers) |
| `connect_timeout` | Connection timeout in seconds | `10` or higher                  |

### Debugging Steps

If you still encounter issues after applying this fix:

1. **Verify connection parameters:**

   ```python
   import psycopg

   # Print connection info (without password)
   conn_info = psycopg.conninfo.conninfo_to_dict(
       "postgresql://user:pass@host:port/db?gssencmode=disable"
   )
   print(conn_info)
   ```
2. **Check libpq version:**

   ```python
   import psycopg
   print(psycopg.pq.version())
   ```
3. **Enable verbose logging:**

   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### Related Issues

- [psycopg GitHub Issue #xxx](https://github.com/psycopg/psycopg/issues)
- [PostgreSQL libpq Documentation](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS)

---

## 🔧 Quick Reference

### Before (Failing on Windows)

```python
conn = psycopg.connect(
    "postgresql://user:pass@host:6543/postgres?sslmode=require"
)
```

### After (Working on Windows)

```python
conn = psycopg.connect(
    "postgresql://user:pass@host:6543/postgres?sslmode=require&gssencmode=disable"
)
```

---

**Last Updated:** November 27, 2025
**Author:** Aryan Singhal
