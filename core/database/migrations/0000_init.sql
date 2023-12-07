CREATE TABLE public.site(
    id uuid not null primary key,
    created_at timestamp with time zone not null,
    url character varying(255) not null,
    visited_at float8 not null
);


