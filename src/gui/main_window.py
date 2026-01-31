"""
Fenêtre principale de TS_Tool_Routier
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTreeWidget,
    QTreeWidgetItem, QSplitter, QTextEdit, QDockWidget,
    QMessageBox, QStatusBar, QTabWidget, QGroupBox,
    QSpinBox, QLineEdit, QFormLayout, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QFont
from core.save_file import SaveFileManager
from core.data_models import GameSave
from utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        self.save_manager = SaveFileManager()
        self.current_save: GameSave = None
        self.modified = False
        
        # Initialisation UI
        self.init_ui()
        self.setup_connections()
        
        logger.info("Interface initialisée")
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("TS_Tool_Routier - Éditeur Transport Fever 2")
        self.setGeometry(100, 100, 1400, 900)
        
        # Police fixe pour l'affichage hexa
        self.fixed_font = QFont("Consolas", 10)
        
        # Créer les composants
        self.create_menu_bar()
        self.create_toolbar()
        self.create_central_widget()
        self.create_status_bar()
        self.create_dock_widgets()
    
    def create_menu_bar(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        
        self.open_action = QAction("&Ouvrir...", self)
        self.open_action.setShortcut("Ctrl+O")
        file_menu.addAction(self.open_action)
        
        self.save_action = QAction("&Enregistrer", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setEnabled(False)
        file_menu.addAction(self.save_action)
        
        self.save_as_action = QAction("Enregistrer &sous...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setEnabled(False)
        file_menu.addAction(self.save_as_action)
        
        file_menu.addSeparator()
        
        self.export_json_action = QAction("Exporter en &JSON...", self)
        self.export_json_action.setEnabled(False)
        file_menu.addAction(self.export_json_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Quitter", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Édition
        edit_menu = menubar.addMenu("&Édition")
        
        self.edit_money_action = QAction("Modifier l'&argent...", self)
        self.edit_money_action.setEnabled(False)
        edit_menu.addAction(self.edit_money_action)
        
        self.unlock_all_action = QAction("&Tout débloquer", self)
        self.unlock_all_action.setEnabled(False)
        edit_menu.addAction(self.unlock_all_action)
        
        # Menu Outils
        tools_menu = menubar.addMenu("&Outils")
        
        self.hex_editor_action = QAction("&Éditeur hexadécimal", self)
        tools_menu.addAction(self.hex_editor_action)
        
        self.find_offset_action = QAction("&Trouver offset...", self)
        tools_menu.addAction(self.find_offset_action)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        
        about_action = QAction("&À propos...", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = self.addToolBar("Outils")
        toolbar.setMovable(False)
        
        # Bouton Ouvrir
        open_btn = QPushButton("Ouvrir")
        open_btn.clicked.connect(self.open_file)
        toolbar.addWidget(open_btn)
        
        # Bouton Enregistrer
        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.clicked.connect(self.save_file)
        self.save_btn.setEnabled(False)
        toolbar.addWidget(self.save_btn)
        
        toolbar.addSeparator()
        
        # Éditeur d'argent rapide
        toolbar.addWidget(QLabel("Argent:"))
        self.money_spinbox = QSpinBox()
        self.money_spinbox.setRange(-1000000000, 10000000000)
        self.money_spinbox.setValue(0)
        self.money_spinbox.setEnabled(False)
        self.money_spinbox.valueChanged.connect(self.on_money_changed)
        toolbar.addWidget(self.money_spinbox)
        
        toolbar.addWidget(QLabel("€"))
    
    def create_central_widget(self):
        """Crée le widget central"""
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panneau gauche: Structure
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Arbre de navigation
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Structure de la sauvegarde")
        self.tree_widget.setFont(self.fixed_font)
        left_layout.addWidget(self.tree_widget)
        
        # Informations du fichier
        info_group = QGroupBox("Informations fichier")
        info_layout = QFormLayout()
        
        self.file_label = QLabel("Aucun fichier chargé")
        self.size_label = QLabel("Taille: -")
        self.version_label = QLabel("Version: -")
        self.money_label = QLabel("Argent: - €")
        
        info_layout.addRow("Fichier:", self.file_label)
        info_layout.addRow("Taille:", self.size_label)
        info_layout.addRow("Version:", self.version_label)
        info_layout.addRow("Argent:", self.money_label)
        
        info_group.setLayout(info_layout)
        left_layout.addWidget(info_group)
        
        left_panel.setLayout(left_layout)
        main_splitter.addWidget(left_panel)
        
        # Panneau central: Éditeurs par onglets
        self.tab_widget = QTabWidget()
        
        # Onglet Éditeur de propriétés
        self.property_editor = QTextEdit()
        self.property_editor.setFont(self.fixed_font)
        self.property_editor.setPlaceholderText("Sélectionnez un élément pour éditer ses propriétés...")
        self.tab_widget.addTab(self.property_editor, "Propriétés")
        
        # Onglet Vue hexadécimale
        from .hex_panel import HexPanel
        self.hex_panel = HexPanel()
        self.tab_widget.addTab(self.hex_panel, "Hexadécimal")
        
        # Onglet Vue carte (à implémenter)
        self.map_viewer = QWidget()
        self.tab_widget.addTab(self.map_viewer, "Carte")
        
        main_splitter.addWidget(self.tab_widget)
        
        # Configuration des tailles
        main_splitter.setSizes([300, 1100])
        
        main_layout.addWidget(main_splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def create_status_bar(self):
        """Crée la barre de statut"""
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Prêt")
        self.setStatusBar(self.status_bar)
        
        # Indicateur de modification
        self.modified_label = QLabel("")
        self.status_bar.addPermanentWidget(self.modified_label)
    
    def create_dock_widgets(self):
        """Crée les panneaux ancrés"""
        # Panneau des modifications récentes
        changes_dock = QDockWidget("Modifications", self)
        changes_widget = QTextEdit()
        changes_widget.setReadOnly(True)
        changes_dock.setWidget(changes_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, changes_dock)
    
    def setup_connections(self):
        """Connecte les signaux et slots"""
        self.open_action.triggered.connect(self.open_file)
        self.save_action.triggered.connect(self.save_file)
        self.save_as_action.triggered.connect(self.save_file_as)
        self.export_json_action.triggered.connect(self.export_json)
        self.edit_money_action.triggered.connect(self.edit_money_dialog)
        self.hex_editor_action.triggered.connect(self.show_hex_editor)
        
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
    
    def open_file(self):
        """Ouvre un fichier de sauvegarde"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir une sauvegarde Transport Fever 2",
            "",
            "Fichiers de sauvegarde (*.save);;Tous les fichiers (*.*)"
        )
        
        if filepath:
            self.load_save_file(filepath)
    
    def load_save_file(self, filepath):
        """Charge et affiche une sauvegarde"""
        try:
            self.current_save = self.save_manager.load_save_file(filepath)
            
            if self.current_save:
                # Mettre à jour l'interface
                self.update_file_info()
                self.populate_tree()
                self.update_money_display()
                
                # Activer les fonctionnalités
                self.save_action.setEnabled(True)
                self.save_as_action.setEnabled(True)
                self.save_btn.setEnabled(True)
                self.export_json_action.setEnabled(True)
                self.edit_money_action.setEnabled(True)
                self.unlock_all_action.setEnabled(True)
                self.money_spinbox.setEnabled(True)
                
                # Charger les données hexa
                self.hex_panel.set_data(self.save_manager.raw_data)
                
                self.status_bar.showMessage(f"Chargé: {os.path.basename(filepath)}")
                self.modified = False
                self.update_modified_indicator()
                
                logger.info(f"Fichier chargé avec succès: {filepath}")
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de charger le fichier")
                
        except Exception as e:
            logger.error(f"Erreur chargement: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement:\n{str(e)}")
    
    def update_file_info(self):
        """Met à jour les informations du fichier"""
        if self.current_save:
            self.file_label.setText(os.path.basename(self.current_save.filepath))
            self.size_label.setText(f"{self.current_save.file_size:,} octets")
            self.version_label.setText(self.current_save.game_version)
    
    def populate_tree(self):
        """Remplit l'arbre de navigation"""
        self.tree_widget.clear()
        
        if not self.current_save:
            return
        
        # Racine: La sauvegarde
        root = QTreeWidgetItem(self.tree_widget, [f"Sauvegarde: {self.current_save.filename}"])
        root.setData(0, Qt.ItemDataRole.UserRole, "save_root")
        
        # Argent
        money_item = QTreeWidgetItem(root, [f"Argent: {self.current_save.money:,} €"])
        money_item.setData(0, Qt.ItemDataRole.UserRole, "money")
        
        # Villes
        cities_item = QTreeWidgetItem(root, [f"Villes ({len(self.current_save.cities)})"])
        for city in self.current_save.cities:
            city_item = QTreeWidgetItem(cities_item, [f"{city.name} (Pop: {city.population:,})"])
            city_item.setData(0, Qt.ItemDataRole.UserRole, ("city", city.id))
        
        # Véhicules
        vehicles_item = QTreeWidgetItem(root, [f"Véhicules ({len(self.current_save.vehicles)})"])
        for vehicle in self.current_save.vehicles:
            vehicle_item = QTreeWidgetItem(vehicles_item, 
                [f"{vehicle.name} ({vehicle.vehicle_type})"])
            vehicle_item.setData(0, Qt.ItemDataRole.UserRole, ("vehicle", vehicle.id))
        
        # Industries
        industries_item = QTreeWidgetItem(root, [f"Industries ({len(self.current_save.industries)})"])
        
        # Développer tout
        self.tree_widget.expandAll()
    
    def update_money_display(self):
        """Met à jour l'affichage de l'argent"""
        if self.current_save:
            self.money_label.setText(f"{self.current_save.money:,} €")
            self.money_spinbox.setValue(self.current_save.money)
    
    def on_money_changed(self, value):
        """Quand l'argent est modifié via le spinbox"""
        if self.current_save and self.current_save.money != value:
            self.current_save.money = value
            self.modified = True
            self.update_modified_indicator()
            self.update_money_display()
            logger.info(f"Argent modifié: {value}")
    
    def save_file(self):
        """Enregistre le fichier courant"""
        if not self.current_save:
            return
        
        success = self.save_manager.save_to_file(self.current_save.filepath)
        
        if success:
            self.modified = False
            self.update_modified_indicator()
            self.status_bar.showMessage(f"Enregistré: {self.current_save.filename}", 3000)
            QMessageBox.information(self, "Succès", "Fichier enregistré avec succès")
        else:
            QMessageBox.warning(self, "Erreur", "Erreur lors de l'enregistrement")
    
    def save_file_as(self):
        """Enregistre sous un nouveau nom"""
        if not self.current_save:
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer sous",
            self.current_save.filepath,
            "Fichiers de sauvegarde (*.save);;Tous les fichiers (*.*)"
        )
        
        if filepath:
            success = self.save_manager.save_to_file(filepath, backup=False)
            if success:
                self.load_save_file(filepath)  # Recharger le nouveau fichier
    
    def export_json(self):
        """Exporte au format JSON"""
        if not self.current_save:
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en JSON",
            f"{self.current_save.filename}.json",
            "Fichiers JSON (*.json);;Tous les fichiers (*.*)"
        )
        
        if filepath:
            self.save_manager.export_to_json(filepath)
            QMessageBox.information(self, "Succès", f"Export JSON réussi:\n{filepath}")
    
    def edit_money_dialog(self):
        """Ouvre une boîte de dialogue pour modifier l'argent"""
        if not self.current_save:
            return
        
        from .money_editor import MoneyEditorDialog
        dialog = MoneyEditorDialog(self.current_save.money, self)
        
        if dialog.exec():
            new_money = dialog.get_value()
            self.current_save.money = new_money
            self.modified = True
            self.update_modified_indicator()
            self.update_money_display()
    
    def show_hex_editor(self):
        """Affiche l'éditeur hexadécimal"""
        self.tab_widget.setCurrentWidget(self.hex_panel)
    
    def on_tree_item_clicked(self, item, column):
        """Quand un élément de l'arbre est cliqué"""
        user_data = item.data(0, Qt.ItemDataRole.UserRole)
        
        if user_data == "money":
            self.property_editor.setText(f"""
            === ARGENT ===
            Valeur: {self.current_save.money:,} €
            Offset: 0x{self.save_manager.known_offsets.get('money_offset', {}).get('offset', 0):08X}
            
            Pour modifier:
            1. Utilisez le spinbox dans la barre d'outils
            2. Ou cliquez sur 'Édition > Modifier l'argent...'
            """)
    
    def update_modified_indicator(self):
        """Met à jour l'indicateur de modification"""
        if self.modified:
            self.modified_label.setText("[MODIFIÉ]")
            self.modified_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.modified_label.setText("")
    
    def show_about(self):
        """Affiche la boîte 'À propos'"""
        about_text = """
        <h2>TS_Tool_Routier</h2>
        <p><b>Version 1.0.0</b></p>
        <p>Éditeur de sauvegardes pour Transport Fever 2</p>
        <p>Développé par [Ton Nom]</p>
        <hr>
        <p>Cet outil permet de modifier les sauvegardes du jeu :</p>
        <ul>
            <li>Modifier l'argent</li>
            <li>Débloquer tous les véhicules</li>
            <li>Éditer les villes et industries</li>
            <li>Visualiser la structure des fichiers</li>
        </ul>
        <p><i>Utilisez avec précaution, toujours faire des sauvegardes !</i></p>
        """
        
        QMessageBox.about(self, "À propos de TS_Tool_Routier", about_text)
    
    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        if self.modified:
            reply = QMessageBox.question(
                self, "Modifications non enregistrées",
                "Vous avez des modifications non enregistrées.\nVoulez-vous vraiment quitter ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        logger.info("Application fermée")
        event.accept()
