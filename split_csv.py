import os

INPUT_FILE = "bgg_boardgames_full_sorted.csv"
# alvo de 99 MB; deixo uma folguinha pra não arriscar o limite do GitHub
MAX_PART_BYTES = 99 * 1024 * 1024       # 99 MB
SAFETY_MARGIN = 512 * 1024              # 512 KB de folga
TARGET_BYTES = MAX_PART_BYTES - SAFETY_MARGIN

OUTPUT_BASENAME = "bgg_boardgames_full_sorted_part"  # part01.csv, part02.csv, ...

def open_new_part(part_idx, header_line):
    fname = f"{OUTPUT_BASENAME}{part_idx:02d}.csv"
    f = open(fname, "w", encoding="utf-8", newline="")
    f.write(header_line)
    return f, fname, len(header_line.encode("utf-8"))

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as fin:
    header = fin.readline()
    if not header:
        raise RuntimeError("CSV sem conteúdo ou sem cabeçalho.")

    part_idx = 1
    fout, current_name, current_bytes = open_new_part(part_idx, header)
    rows_in_part = 0

    for line in fin:
        line_bytes = len(line.encode("utf-8"))

        # se estourar o alvo E já tem ao menos 1 dado escrito, abre nova parte
        if current_bytes + line_bytes > TARGET_BYTES and rows_in_part > 0:
            fout.close()
            print(f"[OK] Fechado {current_name} ({current_bytes/1024/1024:.2f} MB, {rows_in_part} linhas de dados)")
            part_idx += 1
            fout, current_name, current_bytes = open_new_part(part_idx, header)
            rows_in_part = 0

        fout.write(line)
        current_bytes += line_bytes
        rows_in_part += 1

    # fecha última parte
    fout.close()
    print(f"[OK] Fechado {current_name} ({current_bytes/1024/1024:.2f} MB, {rows_in_part} linhas de dados)")

# checagem opcional de tamanhos
for fn in sorted(f for f in os.listdir(".") if f.startswith(OUTPUT_BASENAME) and f.endswith(".csv")):
    sz = os.path.getsize(fn)
    print(f"{fn}: {sz/1024/1024:.2f} MB")
