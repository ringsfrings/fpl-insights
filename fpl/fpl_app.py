"""
Flask application to display Fantasy Premier League (FPL) price changes and differential picks.

This app queries the unofficial FPL API to retrieve player and gameweek data. It
provides two JSON endpoints for price changes and low‑owned differential
recommendations, and a simple frontend for presenting the information. The FPL
API requires no authentication and is publicly accessible. Keep in mind that
access is rate‑limited; consider adding caching in production.

Endpoints:

* `/price_changes` – return players whose price changed in the current gameweek.
* `/differentials` – return low‑owned players (<= 5%) with high form.
* `/` – serve an HTML page with interactive lists for both features.

To run this app:

1. Install dependencies with `pip install flask requests`.
2. Run `python fpl_app.py` and open http://localhost:5000 in your browser.

Note: The FPL API is provided by https://fantasy.premierleague.com and
documentation of endpoints can be found in community articles. The
`bootstrap-static` endpoint returns overall data, including players with
fields such as `now_cost`, `cost_change_event`, `selected_by_percent`,
`form` and `points_per_game`【534315671387406†L61-L99】.
"""

import json
import os
from typing import List, Dict, Any

import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) so that a React frontend
# served from another origin (e.g. localhost:3000) can access these endpoints.
CORS(app)

# FPL endpoints
BOOTSTRAP_STATIC_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"


def fetch_bootstrap_data() -> Dict[str, Any]:
    """Fetch the static bootstrap data from FPL.

    Returns:
        Dict[str, Any]: Parsed JSON response.
    """
    resp = requests.get(BOOTSTRAP_STATIC_URL, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_current_event(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return the best candidate for the current or next gameweek.

    The Fantasy Premier League API marks gameweeks with `is_current` and
    `is_next` flags. To determine the appropriate gameweek we use the
    following logic:

    1. If there is an event with `is_current` true, return it.
    2. Otherwise, if there is an event with `is_next` true, return it.
    3. Otherwise, pick the first event whose deadline_time is in the
       future relative to now (i.e. upcoming gameweek).
    4. If none of the above apply, return the last event.

    Args:
        events (List[Dict[str, Any]]): List of event objects from the FPL API.

    Returns:
        Dict[str, Any]: The selected event.
    """
    # 1. current event
    for event in events:
        if event.get("is_current"):
            return event
    # 2. next event
    for event in events:
        if event.get("is_next"):
            return event
    # 3. first future event by deadline_time
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    for event in events:
        dt_str = event.get("deadline_time")
        if dt_str:
            try:
                dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                if dt > now:
                    return event
            except Exception:
                pass
    # 4. fallback: if we've passed the last event (off-season), return the first event
    # This ensures the app shows the opening gameweek of the upcoming season when
    # there is no `is_current`, `is_next` or future `deadline_time` available (e.g. off-season).
    # If events list is empty, Python will raise IndexError and propagate.
    if events:
        return events[0]
    return {}


@app.route("/price_changes")
def price_changes() -> Any:
    """Return players with price rises or falls during the current gameweek.

    The FPL API provides a `cost_change_event` field on each player which
    indicates their price change in tenths of a million during the current
    gameweek (positive for rises, negative for falls). This endpoint sorts
    players by absolute price change and returns the top N players (default 20).

    Query parameters:
        limit (int, optional): Number of players to return. Default is 20.
    Returns:
        JSON: List of players with price change information.
    """
    limit = int(request.args.get("limit", 20))
    data = fetch_bootstrap_data()
    players = []
    for elem in data["elements"]:
        change = elem.get("cost_change_event", 0)
        if change != 0:
            players.append({
                "id": elem["id"],
                "name": f"{elem['first_name']} {elem['second_name']}",
                "team": elem["team"],
                "position": elem["element_type"],
                "now_cost": elem["now_cost"] / 10.0,
                # Convert change from tenths of a million to millions (e.g. +0.1 or -0.1)
                "price_change": change / 10.0,
                "selected_by_percent": float(elem["selected_by_percent"]),
            })
    # Sort by absolute price change descending, then by change descending
    players.sort(key=lambda x: abs(x["price_change"]), reverse=True)
    top_players = players[:limit]
    return jsonify(top_players)


@app.route("/differentials")
def differentials() -> Any:
    """Return low‑owned players with high recent form.

    A differential is defined here as a player selected by at most 5% of
    managers (adjustable via the `max_ownership` query parameter). We then
    rank these players by their form (a measure provided in the FPL API) and
    return the top N (default 20).

    Query parameters:
        limit (int, optional): Number of players to return. Default is 20.
        max_ownership (float, optional): Maximum ownership percentage
            (selected_by_percent) to qualify as a differential. Default is 5.0.

    Returns:
        JSON: List of differential players with form and ownership.
    """
    limit = int(request.args.get("limit", 20))
    max_own = float(request.args.get("max_ownership", 5.0))
    data = fetch_bootstrap_data()
    players = []
    for elem in data["elements"]:
        # convert string to float
        try:
            ownership = float(elem["selected_by_percent"])
            form = float(elem.get("form", 0) or 0)
            points_per_game = float(elem.get("points_per_game", 0) or 0)
        except ValueError:
            continue
        if ownership <= max_own:
            players.append({
                "id": elem["id"],
                "name": f"{elem['first_name']} {elem['second_name']}",
                "team": elem["team"],
                "position": elem["element_type"],
                "now_cost": elem["now_cost"] / 10.0,
                "ownership": ownership,
                "form": form,
                "points_per_game": points_per_game,
            })
    # Sort by form then points per game
    players.sort(key=lambda x: (x["form"], x["points_per_game"]), reverse=True)
    top_players = players[:limit]
    return jsonify(top_players)


@app.route("/gameweek_overview")
def gameweek_overview() -> Any:
    """Return a summary of the current gameweek.

    The overview includes the event id, name (e.g. "Gameweek 1"),
    average entry score (average points scored by all managers), the highest
    score in the gameweek and chip usage statistics if available. Chip
    usage is returned as a list of objects with `chip_name` and
    `num_played` fields. This data is derived from the FPL API's
    bootstrap-static endpoint, which provides an events array with
    aggregated gameweek information【534315671387406†L61-L99】.

    Returns:
        JSON: Current gameweek overview.
    """
    data = fetch_bootstrap_data()
    events = data.get("events", [])
    if not events:
        return jsonify({}), 503
    current = get_current_event(events)
    overview = {
        "id": current.get("id"),
        "name": current.get("name"),
        "average_entry_score": current.get("average_entry_score"),
        "highest_score": current.get("highest_score"),
        "chip_plays": current.get("chip_plays", []),
    }
    return jsonify(overview)


@app.route("/top_players")
def top_players() -> Any:
    """Return top players sorted by total points.

    Query parameters:
        limit (int, optional): Number of players to return. Default is 10.

    Returns:
        JSON: List of players sorted by total points descending. Each entry
        includes id, name, team, position, now_cost, total_points and
        selected_by_percent.
    """
    limit = int(request.args.get("limit", 10))
    data = fetch_bootstrap_data()
    players = data.get("elements", [])
    # Sort players by total_points descending
    players_sorted = sorted(players, key=lambda e: e.get("total_points", 0), reverse=True)
    result = []
    for elem in players_sorted[:limit]:
        try:
            ownership = float(elem["selected_by_percent"])
        except ValueError:
            ownership = 0.0
        result.append({
            "id": elem["id"],
            "name": f"{elem['first_name']} {elem['second_name']}",
            "team": elem["team"],
            "position": elem["element_type"],
            "now_cost": elem["now_cost"] / 10.0,
            "total_points": elem.get("total_points", 0),
            "selected_by_percent": ownership,
        })
    return jsonify(result)


@app.route("/fixtures")
def fixtures() -> Any:
    """Return upcoming fixtures for the next N gameweeks.

    This endpoint compiles a ticker-like view of upcoming fixtures for all
    teams. Each team entry includes a list of fixtures objects for the
    requested gameweeks. The FPL API provides fixture data via
    `https://fantasy.premierleague.com/api/fixtures/` where each fixture
    record includes fields such as team_h, team_a, event and difficulty
    ratings for both home and away sides.

    Query parameters:
        count (int, optional): Number of upcoming gameweeks to return. Default 6.

    Returns:
        JSON: A dict with keys 'gws' (list of gameweek numbers) and 'data'
        (list of team fixture lists). Each fixture entry has fields:
        opponent (str), home (bool) and difficulty (int 1–5).
    """
    count = int(request.args.get("count", 6))
    # offset parameter allows retrieving fixtures starting a number of gameweeks
    # ahead of the current gameweek (0 = next gameweek).
    offset = int(request.args.get("offset", 0))
    data = fetch_bootstrap_data()
    events = data.get("events", [])
    if not events:
        return jsonify({}), 503
    current_event = get_current_event(events)
    current_id = current_event.get("id")
    # Determine the range of gameweeks
    start_gw = current_id + offset
    end_gw = start_gw + count - 1
    # Map team id to team name
    teams_info = {team["id"]: team["name"] for team in data.get("teams", [])}
    # Initialize structure for each team
    team_data: Dict[int, Dict[int, Any]] = {}
    for tid in teams_info:
        team_data[tid] = {gw: None for gw in range(start_gw, end_gw + 1)}
    # Fetch fixtures from FPL API
    try:
        resp = requests.get("https://fantasy.premierleague.com/api/fixtures/", timeout=30)
        resp.raise_for_status()
        fixtures = resp.json()
    except Exception as e:
        # If API call fails, return empty data
        return jsonify({"gws": [], "data": []})
    # Filter fixtures for our range
    for fixture in fixtures:
        gw = fixture.get("event")
        if gw is None or gw < start_gw or gw > end_gw:
            continue
        home_id = fixture.get("team_h")
        away_id = fixture.get("team_a")
        # Difficulty values
        home_diff = fixture.get("team_h_difficulty")
        away_diff = fixture.get("team_a_difficulty")
        # Record fixture for home team
        if home_id in team_data:
            team_data[home_id][gw] = {
                "opponent": teams_info.get(away_id, ""),
                "home": True,
                "difficulty": home_diff,
            }
        # Record fixture for away team
        if away_id in team_data:
            team_data[away_id][gw] = {
                "opponent": teams_info.get(home_id, ""),
                "home": False,
                "difficulty": away_diff,
            }
    # Build output list
    output = []
    for tid, gw_map in team_data.items():
        output.append({
            "team_name": teams_info.get(tid, ""),
            "fixtures": [gw_map[gw] for gw in range(start_gw, end_gw + 1)],
        })
    return jsonify({"gws": list(range(start_gw, end_gw + 1)), "data": output})


@app.route("/next_fixtures")
def next_fixtures() -> Any:
    """Return detailed fixtures for the current (next) gameweek.

    Each fixture object includes the home and away team names, kickoff time
    (ISO 8601 string) and difficulty ratings for both teams. Difficulty values
    range from 1 (easiest) to 5 (hardest). This endpoint is useful for the
    "Games" section of the frontend where upcoming matches are listed in a
    simple table.

    Returns:
        JSON: List of fixture objects.
    """
    data = fetch_bootstrap_data()
    events = data.get("events", [])
    if not events:
        return jsonify([]), 503
    current_event = get_current_event(events)
    current_id = current_event.get("id")
    # Map team id to name
    teams_info = {team["id"]: team["name"] for team in data.get("teams", [])}
    # Fetch all fixtures and filter by current event
    try:
        resp = requests.get("https://fantasy.premierleague.com/api/fixtures/", timeout=30)
        resp.raise_for_status()
        fixtures = resp.json()
    except Exception:
        return jsonify([])
    result = []
    for fixture in fixtures:
        gw = fixture.get("event")
        if gw != current_id:
            continue
        home_id = fixture.get("team_h")
        away_id = fixture.get("team_a")
        result.append({
            "home_team": teams_info.get(home_id, ""),
            "away_team": teams_info.get(away_id, ""),
            "kickoff_time": fixture.get("kickoff_time"),
            "home_difficulty": fixture.get("team_h_difficulty"),
            "away_difficulty": fixture.get("team_a_difficulty"),
        })
    return jsonify(result)


@app.route("/")
def index() -> Any:
    """Serve the FPL dashboard front page.

    This route serves a React application compiled on the fly via Babel. The
    template `index.html` includes the React code and loads it directly in
    the browser using CDN resources. Running `python3 fpl_app.py` will start
    both the API and the client without requiring a separate Node.js build.
    """
    return render_template("index.html")


if __name__ == "__main__":
    # When running locally the PORT environment variable may not be set. Use 5000
    # as a sane default. Importing os above avoids a NameError here.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)