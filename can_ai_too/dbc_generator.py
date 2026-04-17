def generate_dbc(detected):
    dbc = "VERSION \"AI_GENERATED\"\n\n"

    for i, group in enumerate(detected):
        can_id = group["signals"][0]["id"]

        dbc += f"BO_ {can_id} MSG_{i}: 8 Vector__XXX\n"

        for j, sig in enumerate(group["signals"]):
            dbc += f" SG_ {group['label']}_{j} : {sig['byte']}|8@1+ (1,0) [0|255] \"\" Vector__XXX\n"

        dbc += "\n"

    return dbc
