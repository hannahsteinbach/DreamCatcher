import dreamy

database  = "base"
dream_bank = dreamy.get_HF_DreamBank(database=database, as_dataframe=True)

dream_bank.sample(2)