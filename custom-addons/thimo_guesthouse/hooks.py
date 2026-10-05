def pre_init_hook(env):
    # Trusted PostgreSQL extension: the database owner can install it.
    env.cr.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
