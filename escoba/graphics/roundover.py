
import pygame

from escoba.core.rules import score_round_breakdown

# Colors
BACKGROUND = (51, 153, 112)
PANEL = (28, 65, 51)
GOLD = (235, 199, 125)
WHITE = (255, 255, 255)
ROW_COLOR = (38, 82, 64)


def get_round_scores(game):
    breakdown = score_round_breakdown(game)

    keys = [
        "most_cards",
        "most_oros",
        "most_sevens",
        "velo",
        "escobas",
        "round_total"
    ]

    scores = [
        [entry[key] for entry in breakdown]
        for key in keys
    ]

    scores.append([
        game.player_states[player.id].score
        for player in game.players
    ])

    return scores

    # Reuse the existing award_most function
    def most_points(counts):
        points = [0] * len(states)
        award_most(points, counts)
        return points

    # Points earned in each category
    most_cards = most_points([
        len(state.captured) for state in states
    ])

    most_oros = most_points([
        sum(card.suit == Suit.OROS for card in state.captured)
        for state in states
    ])

    most_sevens = most_points([
        sum(card.rank == 7 for card in state.captured)
        for state in states
    ])

    velo = [
        int(SIETE_DE_VELO in state.captured)
        for state in states
    ]

    escobas = [state.escobas for state in states]

    # Use existing scoring function for round totals
    round_points = score_round(game)

    # Running totals are already updated by end_round()
    total_scores = [state.score for state in states]

    return [
        most_cards,
        most_oros,
        most_sevens,
        velo,
        escobas,
        round_points,
        total_scores
    ]


def draw_round_over(screen, game):
    width, height = screen.get_size()

    # Background
    screen.fill(BACKGROUND)

    # Main menu panel
    panel = pygame.Rect(120, 30, width - 240, height - 60)
    pygame.draw.rect(screen, PANEL, panel, border_radius=15)
    pygame.draw.rect(screen, GOLD, panel, 3, border_radius=15)

    # Fonts
    title_font = pygame.font.SysFont("arial", 42, bold=True)
    header_font = pygame.font.SysFont("arial", 24, bold=True)
    text_font = pygame.font.SysFont("arial", 22)
    bold_font = pygame.font.SysFont("arial", 22, bold=True)

    # ROUND OVER title
    title = title_font.render("ROUND OVER", True, GOLD)
    screen.blit(title, title.get_rect(center=(width // 2, 90)))

    # Subtitle
    subtitle = text_font.render("Round Results", True, WHITE)
    screen.blit(subtitle, subtitle.get_rect(center=(width // 2, 135)))

    # Player headings
    you = header_font.render("YOU", True, GOLD)
    cpu = header_font.render("CPU", True, GOLD)

    screen.blit(you, you.get_rect(center=(570, 185)))
    screen.blit(cpu, cpu.get_rect(center=(735, 185)))

    # Divider
    pygame.draw.line(screen, GOLD, (180, 207), (780, 207), 2)

    # Scoring categories
    categories = [
        "Most Cards",
        "Most Oros",
        "Most Sevens",
        "Siete de Velo",
        "Escobas",
        "Round Points",
        "Total Score"
    ]

    # Get real scores from the game
    scores = get_round_scores(game)

    for i, category in enumerate(categories):
        y = 230 + i * 43

        # Alternating row backgrounds
        if i % 2 == 0:
            row = pygame.Rect(180, y - 19, 600, 38)
            pygame.draw.rect(
                screen, ROW_COLOR, row, border_radius=5
            )

        # Bold totals
        font = bold_font if i >= 5 else text_font
        color = GOLD if i >= 5 else WHITE

        # Category name
        label = font.render(category, True, color)
        screen.blit(label, label.get_rect(midleft=(200, y)))

        # Actual player scores
        you_value = scores[i][0]
        cpu_value = scores[i][1]

        you_score = font.render(str(you_value), True, color)
        cpu_score = font.render(str(cpu_value), True, color)

        screen.blit(
            you_score, you_score.get_rect(center=(570, y))
        )
        screen.blit(
            cpu_score, cpu_score.get_rect(center=(735, y))
        )

    # Bottom divider
    pygame.draw.line(screen, GOLD, (180, 530), (780, 530), 2)

    # Continue message
    continue_text = bold_font.render(
        "Press ENTER to Continue", True, GOLD
    )

    screen.blit(
        continue_text,
        continue_text.get_rect(center=(width // 2, 570))
    )
