import dash_bootstrap_components as dbc
from dash import html, Dash

Agetipa_logo = "/assets/image/logo_agetipa-removebg-preview.png"

def header():
    return dbc.Navbar(
        dbc.Container([
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=Agetipa_logo, height="30px")),
                        dbc.Col(dbc.NavbarBrand("Mobility", className="ms-2 navbar-brand-custom")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Tableau de Bord", href="/bord", className="nav-link-custom", active="exact")),
                    dbc.NavItem(dbc.NavLink("Comparaison des Scénarios", href="/comparaison_scenario", className="nav-link-custom", active="exact")),
                    dbc.NavItem(dbc.NavLink("Analyse Par Commune", href="/analyse_par_commune", className="nav-link-custom", active="exact")),
                    dbc.NavItem(dbc.NavLink("Transport en Commun", href="/transport_en_commun", className="nav-link-custom",
                                            active="exact")),
                    dbc.NavItem(dbc.NavLink("Références", href="/reference", className="nav-link-custom", active="exact")),
                ],
                className="ms-auto",
                navbar=True,

            ),
        ]),
        className="navbar-custom",
        color="#e2e3e5",
        dark=True,
        sticky="top",
    )