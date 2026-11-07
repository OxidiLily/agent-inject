# AiAgents-setup (Windows, Linux, macOS)

Setup adapter/policy tersedia via Windows BAT dan POSIX shell. Instalasi tool lintas platform tersedia melalui `install-tools.py`; Windows wrapper memakai `install-tools.ps1`.

## Mulai cepat

1. Pastikan `SOUL.md` di folder ini berisi policy yang benar.
2. Windows: klik `install-shared-adapters.bat`. Linux/macOS: jalankan `./install-shared-adapters.sh`.
3. Entry point menjalankan adapter/policy, lalu instalasi empat tool.
4. Tutup dan buka ulang agent agar konfigurasi baru dimuat.

Instalasi dapat memasang package software dan memodifikasi user-level skills/channels. Pastikan `winget` (Windows) atau Homebrew (macOS/Linux), `uv`, dan Python tersedia. Bila prasyarat hilang, skrip berhenti dan berikan petunjuk resmi; ia tidak memasang manager itu otomatis.

Argumen target opsional diteruskan ke installer, misalnya jalankan dari CMD/PowerShell: `install-shared-adapters.bat codex`. Untuk menjalankan injeksi saja, `inject-agent-policy.bat` tetap tersedia.

## File utama

- `install-shared-adapters.bat`: launcher Windows; jalankan adapter, injeksi policy, lalu pemasangan tools.
- `install-shared-adapters.sh`: launcher Linux/macOS untuk pemasangan tools.
- `install-tools.py`: installer tools lintas OS.
- `install-tools.ps1`: wrapper Windows.
- `inject-agent-policy.ps1`: menyisipkan atau memperbarui blok policy bertanda.
- `inject-agent-policy.bat`: menjalankan injeksi saja.
- `SOUL.md`: policy kanonis yang dibaca agent.
- `grounded-search.py`: pencarian dan pencatatan Sessions.
- `Sessions/`, `Skills/`, `knowledge-base.md`: state bersama.
- `kredensial/`: manifest dan secret store lokal; jangan bagikan atau commit secret.
- `install-shared-adapters.ps1`: menyiapkan adapter untuk agent terdeteksi (Windows).
- `install-shared-adapters.sh`: launcher POSIX; menjalankan installer tools.
- `PROMPT-DEPLOY-SHARED.md`: prompt deployment; tidak dipanggil skrip Windows.

Jangan hapus `SOUL.md`, `grounded-search.py`, `Sessions/`, `Skills/`, `knowledge-base.md`, atau `kredensial/`: skrip/policy merujuknya. File `.ps1` juga diperlukan sebagai implementasi yang dipanggil BAT. `inject-agent-policy.bat` opsional bila selalu memakai BAT gabungan.

## Target konfigurasi

- Hermes: `$env:HERMES_HOME` jika disetel; default injektor `C:\Users\<user>\AppData\Local\hermes`.
- Claude Code: `$HOME\.claude\CLAUDE.md`.
- Codex: `$env:CODEX_HOME\AGENTS.md` jika disetel; jika tidak `$HOME\.codex\AGENTS.md`.
- OpenCode: `$HOME\.config\opencode\AGENTS.md`.
- OpenClaw: `$env:OPENCLAW_WORKSPACE` jika disetel; jika tidak `$HOME\.openclaw\workspace\AGENTS.md` dan `SOUL.md`.

Shared state berada di folder setup ini. `LAST_RITE_SETUP_ROOT` dapat mengubah root yang dipakai adapter installer. `inject-agent-policy.ps1` menerima `-TargetHome` untuk home alternatif.

## Persyaratan dan batasan

- Windows: PowerShell 5.1+, Python 3.10+, winget, uv.
- macOS/Linux: Python 3.10+, Homebrew, uv; launcher `install-shared-adapters.sh`.
- Skrip tidak memasang package manager atau uv bila hilang. Ikuti URL instalasi resmi yang dicetak, lalu jalankan ulang.
- Adapter hanya dibuat bila executable agent terdeteksi. POSIX launcher saat ini memasang tools; belum mem-port adapter/policy injection PowerShell.
- Installer memasang RTK, Browser Use CLI + skill, Agent Reach defaults + skill, dan mengunduh 9Router skill ke shared Skills.
- Tidak memasang cloud credentials, logins, atau API keys.
- Setiap tahap memverifikasi command bila tersedia. Kegagalan menghentikan alur; package yang sudah terpasang tidak otomatis di-rollback.
- Browser Use dan Agent Reach setup dapat mengubah user-level skill/channel files. Review hasil dan mulai ulang agent bila perlu.

## Helper sesi manual

```powershell
python .\grounded-search.py search "kata kunci" --root $PWD
python .\grounded-search.py record --root $PWD --agent hermes --topic "Topik" --question "Pertanyaan ringkas" --answer "Jawaban ringkas" --sources "URL atau sumber"
```

Jangan catat password, token, atau secret. Policy menginstruksikan agent memakai helper; helper tidak berjalan otomatis di latar belakang.

## Verifikasi

```powershell
Test-Path .\grounded-search.py
python .\grounded-search.py search "kata kunci uji" --root $PWD
Select-String -Path "$HOME\AppData\Local\hermes\SOUL.md" -Pattern 'MULAI linux-dashboard'
```

Pencarian tanpa hasil menampilkan pesan informatif; itu bukan error.
