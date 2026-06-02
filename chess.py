from abc import ABC, abstractmethod
import random
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os

DOSSIER_IMAGES = "c:/Users/bodin/chess_Hippolyte/images/images/"  # à adapter selon votre système

# ============================================================
# CLASSE Position
# ============================================================
class Position:
    def __init__(self, column, row):
        self._column = column  # lettre : 'a' à 'h'
        self._row = row        # entier : 1 à 8

    @property
    def column(self):
        return self._column

    @property
    def row(self):
        return self._row

    def __str__(self):
        return f"{self._column}{self._row}"

    def __eq__(self, other):
        if other is None:
            return False
        return self._column == other._column and self._row == other._row


# ============================================================
# CLASSE ABSTRAITE Piece
# ============================================================
class Piece(ABC):
    def __init__(self, color, position):
        self._color = color        # 0 = blanc, 1 = noir
        self._position = position  # type Position

    @property
    def color(self):
        return self._color

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_pos):
        self._position = new_pos

    @abstractmethod
    def isValidMove(self, newPosition, board):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def _is_same_color_at(self, newPosition, board):
        target = board.getPiece(newPosition)
        if target is not None and target.color == self._color:
            return True
        return False

    def _col_to_int(self, col):
        return ord(col) - ord('a') + 1


# ============================================================
# LES 6 TYPES DE PIECES
# ============================================================

class King(Piece):
    def __str__(self): 
        return 'K'
    def isValidMove(self, newPosition, board):
        if self._is_same_color_at(newPosition, board): return False
        col_diff = abs(self._col_to_int(newPosition.column) - self._col_to_int(self._position.column))
        row_diff = abs(newPosition.row - self._position.row)
        return col_diff <= 1 and row_diff <= 1 and (col_diff + row_diff) > 0

class Queen(Piece):
    def __str__(self): 
        return 'Q'
    def isValidMove(self, newPosition, board):
        if self._is_same_color_at(newPosition, board): return False
        col_diff = self._col_to_int(newPosition.column) - self._col_to_int(self._position.column)
        row_diff = newPosition.row - self._position.row
        if col_diff == 0 or row_diff == 0 or abs(col_diff) == abs(row_diff):
            return not board.isPathBlocked(self._position, newPosition)
        return False

class Bishop(Piece):
    def __str__(self): 
        return 'B'
    def isValidMove(self, newPosition, board):
        if self._is_same_color_at(newPosition, board): return False
        col_diff = abs(self._col_to_int(newPosition.column) - self._col_to_int(self._position.column))
        row_diff = abs(newPosition.row - self._position.row)
        if col_diff == row_diff and col_diff > 0:
            return not board.isPathBlocked(self._position, newPosition)
        return False

class Knight(Piece):
    def __str__(self): 
        return 'N'
    def isValidMove(self, newPosition, board):
        if self._is_same_color_at(newPosition, board): return False
        col_diff = abs(self._col_to_int(newPosition.column) - self._col_to_int(self._position.column))
        row_diff = abs(newPosition.row - self._position.row)
        return (col_diff == 2 and row_diff == 1) or (col_diff == 1 and row_diff == 2)

class Rook(Piece):
    def __str__(self): 
        return 'R'
    def isValidMove(self, newPosition, board):
        if self._is_same_color_at(newPosition, board): return False
        col_diff = self._col_to_int(newPosition.column) - self._col_to_int(self._position.column)
        row_diff = newPosition.row - self._position.row
        if (col_diff == 0 or row_diff == 0) and (col_diff != 0 or row_diff != 0):
            return not board.isPathBlocked(self._position, newPosition)
        return False

class Pawn(Piece):
    def __str__(self): 
        return 'P'
    def isValidMove(self, newPosition, board):
        if self._is_same_color_at(newPosition, board): return False
        direction = 1 if self._color == 0 else -1
        start_row = 2 if self._color == 0 else 7
        col_diff = self._col_to_int(newPosition.column) - self._col_to_int(self._position.column)
        row_diff = newPosition.row - self._position.row
        if col_diff == 0 and row_diff == direction:
            return board.getPiece(newPosition) is None
        if col_diff == 0 and row_diff == 2 * direction and self._position.row == start_row:
            middle = Position(self._position.column, self._position.row + direction)
            return board.getPiece(middle) is None and board.getPiece(newPosition) is None
        if abs(col_diff) == 1 and row_diff == direction:
            return board.getPiece(newPosition) is not None
        return False


# ============================================================
# CLASSE Board
# ============================================================
class Board:
    def __init__(self):
        self._grid = {}
        self._initBoard()

    def _initBoard(self):
        columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for col in columns:
            for row in range(1, 9):
                self._grid[f"{col}{row}"] = None
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, col in enumerate(columns):
            self._grid[f"{col}1"] = piece_order[i](0, Position(col, 1))
            self._grid[f"{col}2"] = Pawn(0, Position(col, 2))
            self._grid[f"{col}8"] = piece_order[i](1, Position(col, 8))
            self._grid[f"{col}7"] = Pawn(1, Position(col, 7))

    def getPiece(self, position):
        return self._grid.get(str(position), None)

    def getPosition(self, piece):
        for key, p in self._grid.items():
            if p is piece:
                return p.position
        return None

    def isPathBlocked(self, fromPos, toPos):
        col_start = ord(fromPos.column) - ord('a') + 1
        col_end   = ord(toPos.column)   - ord('a') + 1
        row_start, row_end = fromPos.row, toPos.row
        col_step = 0 if col_end == col_start else (1 if col_end > col_start else -1)
        row_step = 0 if row_end == row_start else (1 if row_end > row_start else -1)
        col, row = col_start + col_step, row_start + row_step
        while (col, row) != (col_end, row_end):
            if self.getPiece(Position(chr(ord('a') + col - 1), row)) is not None:
                return True
            col += col_step
            row += row_step
        return False

    def movePiece(self, fromPos, toPos):
        piece = self._grid[str(fromPos)]
        self._grid[str(toPos)] = piece
        self._grid[str(fromPos)] = None
        piece.position = toPos

    def to_dict(self):
        data = {}
        piece_names = {King: 'King', Queen: 'Queen', Bishop: 'Bishop',
                       Knight: 'Knight', Rook: 'Rook', Pawn: 'Pawn'}
        for key, piece in self._grid.items():
            if piece is not None:
                data[key] = {'type': piece_names[type(piece)], 'color': piece.color}
        return data

    def from_dict(self, data):
        piece_classes = {'King': King, 'Queen': Queen, 'Bishop': Bishop,
                         'Knight': Knight, 'Rook': Rook, 'Pawn': Pawn}
        columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for col in columns:
            for row in range(1, 9):
                self._grid[f"{col}{row}"] = None
        for key, info in data.items():
            col, row = key[0], int(key[1])
            pos = Position(col, row)
            self._grid[key] = piece_classes[info['type']](info['color'], pos)


# ============================================================
# CLASSE Player
# ============================================================
class Player:
    def __init__(self, name, color):
        self._name = name
        self._color = color

    @property
    def name(self): return self._name

    @property
    def color(self): return self._color


class AIPlayer(Player):
    def __init__(self, name, color):
        super().__init__(name, color)


# ============================================================
# CLASSE Chess
# ============================================================
class Chess:
    PIECE_LETTERS = {'K': King, 'Q': Queen, 'B': Bishop, 'N': Knight, 'R': Rook, 'P': Pawn}

    def __init__(self):
        self._board = Board()
        self._players = []
        self._currentPlayer = None

    @property
    def board(self): return self._board

    @property
    def currentPlayer(self): return self._currentPlayer

    def initPlayers(self, name1, name2):
        color0 = AIPlayer(name1, 0) if name1 == "AI" else Player(name1, 0)
        color1 = AIPlayer(name2, 1) if name2 == "AI" else Player(name2, 1)
        self._players = [color0, color1]
        self._currentPlayer = self._players[0]

    def isValidMove(self, fromPos, toPos):
        piece = self._board.getPiece(fromPos)
        if piece is None: return False
        if piece.color != self._currentPlayer.color: return False
        return piece.isValidMove(toPos, self._board)

    def updateBoard(self, fromPos, toPos):
        self._board.movePiece(fromPos, toPos)

    def switchPlayer(self):
        self._currentPlayer = self._players[1] if self._currentPlayer == self._players[0] else self._players[0]

    def isCheckMate(self):
        return False

    def generateRandomMove(self):
        columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        my_pieces = []
        for col in columns:
            for row in range(1, 9):
                p = self._board.getPiece(Position(col, row))
                if p is not None and p.color == self._currentPlayer.color:
                    my_pieces.append(p)
        random.shuffle(my_pieces)
        for piece in my_pieces:
            cols = columns[:]
            rows = list(range(1, 9))
            random.shuffle(cols)
            random.shuffle(rows)
            for col in cols:
                for row in rows:
                    to_pos = Position(col, row)
                    if piece.isValidMove(to_pos, self._board):
                        return piece.position, to_pos
        return None, None

    def saveGame(self, filename="sauvegarde.json"):
        data = {
            'board': self._board.to_dict(),
            'players': [{'name': p.name, 'color': p.color, 'is_ai': isinstance(p, AIPlayer)} for p in self._players],
            'current_player_color': self._currentPlayer.color
        }
        with open(filename, 'w') as f:
            json.dump(data, f)

    def loadGame(self, filename="sauvegarde.json"):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self._board.from_dict(data['board'])
            self._players = []
            for p in data['players']:
                cls = AIPlayer if p['is_ai'] else Player
                self._players.append(cls(p['name'], p['color']))
            self._currentPlayer = next(p for p in self._players if p.color == data['current_player_color'])
            return True
        except FileNotFoundError:
            return False


# ============================================================
# INTERFACE GRAPHIQUE TKINTER
# ============================================================
class ChessGUI:
    CELL_SIZE = 75
    COLUMNS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    # Couleurs du plateau
    COLOR_LIGHT  = "#F0D9B5"
    COLOR_DARK   = "#B58863"
    COLOR_SELECT = "#7FC97F"   # case sélectionnée (vert)
    COLOR_VALID  = "#6699CC"   # cases de destination valides (bleu)

    def __init__(self, root):
        self._root = root
        self._root.title("Jeu d'Échecs")
        self._game = Chess()
        self._images = {}          # dictionnaire : clé = "Kw" -> PhotoImage
        self._selected_pos = None  # Position sélectionnée par le joueur
        self._valid_moves = []     # liste de positions valides

        self._load_images()
        self._build_ui()
        self._ask_players()

    def _load_images(self):
        """Charge les images des pièces depuis le dossier images/."""
        piece_map = {'K': 'K', 'Q': 'Q', 'B': 'B', 'N': 'N', 'R': 'R', 'P': 'P'}
        color_map = {0: 'w', 1: 'b'}
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(base_dir, "images", 'images')

        for letter in piece_map:
            for color_int, color_char in color_map.items():
                filename = os.path.join(img_dir, f"{letter}{color_char}.png")
                try:
                    img = Image.open(filename).resize((self.CELL_SIZE - 10, self.CELL_SIZE - 10))
                    self._images[f"{letter}{color_int}"] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Image non trouvée : {filename} ({e})")

    def _build_ui(self):
        """Construit l'interface : plateau + barre de statut + boutons."""
        # Cadre principal
        main_frame = tk.Frame(self._root, bg="#2C2C2C")
        main_frame.pack(padx=10, pady=10)

        # Canvas du plateau
        board_size = self.CELL_SIZE * 8
        self._canvas = tk.Canvas(main_frame, width=board_size + 40, height=board_size + 40, bg="#2C2C2C")
        self._canvas.pack()
        self._canvas.bind("<Button-1>", self._on_click)

        # Barre de statut
        self._status_var = tk.StringVar(value="Bienvenue !")
        status_bar = tk.Label(self._root, textvariable=self._status_var,
                              font=("Arial", 13), bg="#2C2C2C", fg="white", pady=6)
        status_bar.pack(fill=tk.X)

        # Boutons
        btn_frame = tk.Frame(self._root, bg="#2C2C2C")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="💾 Sauvegarder", command=self._save,
                  font=("Arial", 11), bg="#4CAF50", fg="white", padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📂 Charger", command=self._load,
                  font=("Arial", 11), bg="#2196F3", fg="white", padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔄 Nouvelle partie", command=self._new_game,
                  font=("Arial", 11), bg="#FF5722", fg="white", padx=10).pack(side=tk.LEFT, padx=5)

    def _ask_players(self):
        """Demande les noms des joueurs via des boîtes de dialogue."""
        name1 = simpledialog.askstring("Joueur Blanc", "Nom du joueur Blanc (ou 'AI') :", initialvalue="Joueur 1")
        if not name1: name1 = "Joueur 1"
        name2 = simpledialog.askstring("Joueur Noir", "Nom du joueur Noir (ou 'AI') :", initialvalue="Joueur 2")
        if not name2: name2 = "Joueur 2"
        self._game.initPlayers(name1, name2)
        self._refresh()

    def _canvas_to_pos(self, x, y):
        """Convertit les coordonnées du clic en Position."""
        offset = 20  # marge pour les labels
        col_idx = (x - offset) // self.CELL_SIZE
        row_idx = (y - offset) // self.CELL_SIZE
        if 0 <= col_idx <= 7 and 0 <= row_idx <= 7:
            col = self.COLUMNS[col_idx]
            row = 8 - row_idx  # row 8 en haut, row 1 en bas
            return Position(col, row)
        return None

    def _pos_to_canvas(self, pos):
        """Convertit une Position en coordonnées canvas (coin haut-gauche de la case)."""
        offset = 20
        col_idx = self.COLUMNS.index(pos.column)
        row_idx = 8 - pos.row
        x = offset + col_idx * self.CELL_SIZE
        y = offset + row_idx * self.CELL_SIZE
        return x, y

    def _get_valid_moves(self, fromPos):
        """Retourne toutes les positions valides pour la pièce à fromPos."""
        valid = []
        for col in self.COLUMNS:
            for row in range(1, 9):
                to_pos = Position(col, row)
                if self._game.isValidMove(fromPos, to_pos):
                    valid.append(to_pos)
        return valid

    def _draw_board(self):
        """Dessine le plateau (cases colorées + labels)."""
        self._canvas.delete("all")
        offset = 20

        # Labels colonnes (a-h)
        for i, col in enumerate(self.COLUMNS):
            x = offset + i * self.CELL_SIZE + self.CELL_SIZE // 2
            self._canvas.create_text(x, 10, text=col, fill="white", font=("Arial", 11, "bold"))
            self._canvas.create_text(x, offset + 8 * self.CELL_SIZE + 10, text=col, fill="white", font=("Arial", 11, "bold"))

        # Labels rangées (1-8)
        for row in range(1, 9):
            y = offset + (8 - row) * self.CELL_SIZE + self.CELL_SIZE // 2
            self._canvas.create_text(10, y, text=str(row), fill="white", font=("Arial", 11, "bold"))
            self._canvas.create_text(offset + 8 * self.CELL_SIZE + 10, y, text=str(row), fill="white", font=("Arial", 11, "bold"))

        # Cases
        for col_idx, col in enumerate(self.COLUMNS):
            for row in range(1, 9):
                pos = Position(col, row)
                x, y = self._pos_to_canvas(pos)

                # Couleur de base
                if (col_idx + row) % 2 == 0:
                    color = self.COLOR_DARK
                else:
                    color = self.COLOR_LIGHT

                # Surbrillance sélection
                if self._selected_pos and pos == self._selected_pos:
                    color = self.COLOR_SELECT
                elif any(pos == vp for vp in self._valid_moves):
                    color = self.COLOR_VALID

                self._canvas.create_rectangle(x, y, x + self.CELL_SIZE, y + self.CELL_SIZE,
                                              fill=color, outline="")

    def _draw_pieces(self):
        """Dessine les pièces sur le plateau."""
        for col in self.COLUMNS:
            for row in range(1, 9):
                pos = Position(col, row)
                piece = self._game.board.getPiece(pos)
                if piece is not None:
                    key = f"{str(piece)}{piece.color}"
                    img = self._images.get(key)
                    if img:
                        x, y = self._pos_to_canvas(pos)
                        cx = x + self.CELL_SIZE // 2
                        cy = y + self.CELL_SIZE // 2
                        self._canvas.create_image(cx, cy, image=img)

    def _refresh(self):
        """Redessine tout le plateau."""
        self._draw_board()
        self._draw_pieces()
        player = self._game.currentPlayer
        color_name = "Blanc" if player.color == 0 else "Noir"
        self._status_var.set(f"Tour de {player.name} ({color_name})")

        # Si c'est le tour de l'IA, jouer automatiquement
        if isinstance(player, AIPlayer):
            self._root.after(500, self._ai_play)

    def _on_click(self, event):
        """Gère le clic sur le plateau."""
        # Ignorer si c'est le tour de l'IA
        if isinstance(self._game.currentPlayer, AIPlayer):
            return

        pos = self._canvas_to_pos(event.x, event.y)
        if pos is None:
            return

        if self._selected_pos is None:
            # Premier clic : sélectionner une pièce
            piece = self._game.board.getPiece(pos)
            if piece is not None and piece.color == self._game.currentPlayer.color:
                self._selected_pos = pos
                self._valid_moves = self._get_valid_moves(pos)
                self._refresh()
        else:
            # Deuxième clic : déplacer
            if self._game.isValidMove(self._selected_pos, pos):
                self._game.updateBoard(self._selected_pos, pos)
                self._selected_pos = None
                self._valid_moves = []
                self._game.switchPlayer()
                self._refresh()
            else:
                # Clic sur une autre pièce alliée : changer la sélection
                piece = self._game.board.getPiece(pos)
                if piece is not None and piece.color == self._game.currentPlayer.color:
                    self._selected_pos = pos
                    self._valid_moves = self._get_valid_moves(pos)
                else:
                    self._selected_pos = None
                    self._valid_moves = []
                self._refresh()

    def _ai_play(self):
        """Fait jouer l'IA."""
        from_pos, to_pos = self._game.generateRandomMove()
        if from_pos and to_pos:
            self._game.updateBoard(from_pos, to_pos)
            self._game.switchPlayer()
        self._refresh()

    def _save(self):
        self._game.saveGame()
        messagebox.showinfo("Sauvegarde", "Partie sauvegardée !")

    def _load(self):
        if self._game.loadGame():
            self._selected_pos = None
            self._valid_moves = []
            self._refresh()
            messagebox.showinfo("Chargement", "Partie chargée !")
        else:
            messagebox.showerror("Erreur", "Aucune sauvegarde trouvée.")

    def _new_game(self):
        self._game = Chess()
        self._selected_pos = None
        self._valid_moves = []
        self._ask_players()


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#2C2C2C")
    app = ChessGUI(root)
    root.mainloop()