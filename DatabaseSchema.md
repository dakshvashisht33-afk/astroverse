# Database Schema: AstroVerse (PostgreSQL)

## 1. Core User Entities
- **`users`**
    - `id` (UUID, PK)
    - `email` (Unique, Indexed)
    - `password_hash` (Argon2id)
    - `oauth_provider` (Enum: google, apple, none)
    - `oauth_id` (Unique)
    - `phone_number` (Unique, Optional)
    - `role` (Enum: user, astrologer, editor, admin, super_admin)
    - `created_at`, `updated_at`

- **`profiles`**
    - `id` (UUID, PK)
    - `user_id` (FK $\rightarrow$ users.id)
    - `full_name` (String)
    - `gender` (String, Optional)
    - `language_preference` (String, Default: 'en')
    - `preferred_system` (Enum: vedic, western, both)
    - `created_at`, `updated_at`

- **`birth_profiles`** (Allows multiple profiles per user)
    - `id` (UUID, PK)
    - `profile_id` (FK $\rightarrow$ profiles.id)
    - `label` (String, e.g., "Me", "Partner", "Child")
    - `dob` (Date)
    - `tob` (Time)
    - `tob_unknown` (Boolean)
    - `birth_city` (String)
    - `latitude` (Decimal)
    - `longitude` (Decimal)
    - `timezone` (String)
    - `created_at`

---

## 2. Astrology Data Entities
- **`chart_calculations`** (Caches expensive ephemeris results)
    - `id` (UUID, PK)
    - `birth_profile_id` (FK $\rightarrow$ birth_profiles.id)
    - `calculation_type` (Enum: natal, transit, solar_return)
    - `system` (Enum: vedic, western)
    - `ayanamsa` (String)
    - `house_system` (String)
    - `planetary_data` (JSONB - stores exact degrees, signs, and houses)
    - `calculated_at` (Timestamp)

- **`horoscopes`**
    - `id` (UUID, PK)
    - `sign` (String, e.g., "Aries")
    - `period` (Enum: daily, weekly, monthly, yearly)
    - `type` (Enum: sun, moon, ascendant)
    - `content` (Text/Markdown)
    - `published_at` (Timestamp)
    - `expires_at` (Timestamp)

---

## 3. AI & Conversation Entities
- **`ai_conversations`**
    - `id` (UUID, PK)
    - `user_id` (FK $\rightarrow$ users.id)
    - `birth_profile_id` (FK $\rightarrow$ birth_profiles.id)
    - `title` (String)
    - `created_at`, `updated_at`

- **`ai_messages`**
    - `id` (UUID, PK)
    - `conversation_id` (FK $\rightarrow$ ai_conversations.id)
    - `role` (Enum: user, assistant, system)
    - `content` (Text)
    - `tokens_used` (Integer)
    - `latency_ms` (Integer)
    - `created_at`

---

## 4. Marketplace & Financial Entities
- **`astrologers`**
    - `id` (UUID, PK)
    - `user_id` (FK $\rightarrow$ users.id)
    - `bio` (Text)
    - `specialties` (Array[String])
    - `price_per_minute` (Decimal)
    - `rating` (Decimal)
    - `is_verified` (Boolean)

- **`consultations`**
    - `id` (UUID, PK)
    - `user_id` (FK $\rightarrow$ users.id)
    - `astrologer_id` (FK $\rightarrow$ astrologers.id)
    - `scheduled_at` (Timestamp)
    - `duration_minutes` (Integer)
    - `status` (Enum: pending, confirmed, completed, cancelled)
    - `payment_status` (Enum: unpaid, paid, refunded)

- **`wallets`**
    - `id` (UUID, PK)
    - `user_id` (FK $\rightarrow$ users.id)
    - `balance` (Decimal)
    - `currency` (String)

- **`transactions`**
    - `id` (UUID, PK)
    - `wallet_id` (FK $\rightarrow$ wallets.id)
    - `amount` (Decimal)
    - `type` (Enum: credit, debit)
    - `provider_transaction_id` (String)
    - `created_at`
