export default {
  common: {
    save: 'Enregistrer',
    cancel: 'Annuler',
    delete: 'Supprimer',
    edit: 'Modifier',
    add: 'Ajouter',
    confirm: 'Confirmer',
    minutes: 'Minutes',
    loading: 'Chargement...',
    success: 'Succès',
    error: 'Erreur',
    warning: 'Avertissement',
    info: 'Info',
    menu: 'Menu',
    systemName: 'AI demo HUB'
  },
  settings: {
    system: {
      title: 'Configuration du Système',
      language: 'Langue du Système',
      autoSaveInterval: 'Intervalle de Sauvegarde Automatique',
      dataRetention: 'Conservation des Données',
      alarmThreshold: 'Seuil d\'Alarme'
    },
    mes: {
      title: 'Intégration MES',
      serverUrl: 'Adresse du Serveur',
      apiKey: 'Clé API',
      testConnection: 'Tester la Connexion'
    },
    devices: {
      title: 'Gestion des Appareils',
      all: 'Tous',
      camera: 'Caméra',
      light: 'Éclairage',
      plc: 'Contrôleur',
      disableAutoCheck: 'Désactiver la Vérification Automatique',
      refreshStatus: 'Actualiser l\'État des Appareils',
      addDevice: 'Ajouter un Appareil',
      status: {
        online: 'En ligne',
        offline: 'Hors ligne',
        error: 'Erreur',
        unknown: 'Inconnu'
      },
      preview: {
        setOnline: 'Mettre en Ligne',
        setOffline: 'Mettre Hors Ligne',
        edit: 'Modifier l\'Appareil',
        delete: 'Supprimer l\'Appareil',
        title: 'Aperçu de {name}',
        status: 'État de la Caméra',
        streamUrl: 'URL du Flux',
        notConfigured: 'Non Configuré'
      },
      form: {
        title: {
          add: 'Ajouter un Appareil',
          edit: 'Modifier un Appareil'
        },
        name: 'Nom de l\'Appareil',
        type: 'Type d\'Appareil',
        model: 'Modèle d\'Appareil',
        config: 'Configuration de l\'Appareil',
        camera: {
          type: 'Type de Caméra',
          types: {
            local: 'Caméra Locale',
            ip: 'Caméra IP',
            rtsp: 'Flux RTSP',
            http: 'Flux HTTP'
          },
          deviceId: 'ID de l\'Appareil',
          streamUrl: 'URL de la Caméra'
        },
        light: {
          port: 'Port Série',
          mode: 'Mode de Fonctionnement',
          modes: {
            continuous: 'Continu',
            flash: 'Flash',
            trigger: 'Déclenchement'
          }
        },
        plc: {
          ip: 'Adresse IP',
          rack: 'Numéro de Rack',
          slot: 'Numéro de Slot'
        }
      },
      noDevices: 'Aucun appareil {type}',
      deleteConfirm: 'Êtes-vous sûr de vouloir supprimer l\'appareil "{name}" ?',
      type: {
        camera: 'Caméra',
        light: 'Éclairage',
        plc: 'Contrôleur'
      }
    },
    notifications: {
      savingSettings: 'Enregistrement des paramètres système...',
      settingsSaved: 'Paramètres système enregistrés',
      savingFailed: 'Échec de l\'enregistrement des paramètres système',
      savingMes: 'Enregistrement des paramètres MES...',
      mesSaved: 'Paramètres MES enregistrés',
      mesSavingFailed: 'Échec de l\'enregistrement des paramètres MES',
      loadDevicesFailed: 'Échec du chargement de la liste des appareils',
      deviceUpdated: 'Appareil mis à jour',
      deviceAdded: 'Appareil ajouté',
      deviceDeleted: 'Appareil supprimé',
      deviceSaveFailed: 'Échec de l\'enregistrement de l\'appareil',
      deviceDeleteFailed: 'Échec de la suppression de l\'appareil',
      cameraIdError: 'Échec de l\'obtention de l\'ID de la caméra, veuillez vérifier la configuration',
      deviceStatusChanged: '{name} {status}',
      deviceStatusUpdateFailed: 'Échec de la mise à jour de l\'état de l\'appareil',
      loadSettingsFailed: 'Échec du chargement des paramètres système',
      loadMesFailed: 'Échec du chargement des paramètres MES',
      languageChanged: 'Langue modifiée'
    }
  },
  status: {
    cameraList: 'Liste des Caméras',
    noCameras: 'Aucune caméra configurée',
    camera: 'Caméra',
    modelList: 'Liste des Modèles',
    noModels: 'Aucun modèle chargé',
    model: 'Modèle',
    deviceList: 'Liste des Appareils',
    noDevices: 'Aucun appareil de contrôle configuré',
    device: 'Appareil',
    online: 'En ligne',
    offline: 'Hors ligne',
    error: 'Erreur',
    connected: 'Connecté',
    disconnected: 'Déconnecté',
    partiallyConnected: 'Partiellement Connecté',
    loaded: 'Chargé',
    notLoaded: 'Non Chargé'
  },
  emergencyStop: {
    title: 'Arrêt d\'Urgence',
    message: 'Confirmer l\'exécution de l\'arrêt d\'urgence ? Cela arrêtera toutes les opérations des appareils.',
    confirm: 'Confirmer l\'Arrêt',
    executed: 'Opération d\'arrêt d\'urgence exécutée'
  },
  routes: {
    dashboard: 'Tableau de Bord',
    realtime: 'Surveillance en Temps Réel',
    history: 'Historique',
    annotation: 'Annotation de Données',
    model: 'Entraînement de Modèle',
    modelTest: 'Test de Modèle',
    cvOperations: 'Traitement d\'Image',
    settings: 'Paramètres',
    notFound: 'Page Non Trouvée'
  },
  dashboard: {
    systemStatus: {
      title: 'État du Système',
      uptime: 'Temps de Fonctionnement',
      memory: 'Mémoire',
      disk: 'Disque',
      systemNormal: 'Système Normal',
      systemLoadHigh: 'Charge Système Élevée',
      systemResourceStress: 'Stress des Ressources Système',
      systemStatusError: 'Erreur d\'État du Système',
      days: 'JOURS ',
      hours: 'HEURES ',
      minutes: 'MINUTES ',
      seconds: 'SECONDES ',
      unknown:'INCONNU'
    },
    deviceStatus: {
      title: 'État des Appareils',
      onlineRate: 'Taux de Disponibilité',
      total: 'Total',
      online: 'En ligne',
      offline: 'Hors ligne',
      error: 'Erreur',
      cameras: 'Caméras'
    },
    detectionStats: {
      title: 'Statistiques de Détection d\'Aujourd\'hui',
      comparedToYesterday: 'Par rapport à hier ({count}) {change}',
      increase: 'augmentation',
      decrease: 'diminution'
    },
    defectStats: {
      title: 'Statistiques de Défauts d\'Aujourd\'hui',
      comparedToYesterday: 'Par rapport à hier ({count}) {change}',
      increase: 'augmentation',
      decrease: 'diminution'
    },
    accuracy: {
      title: 'Précision de Détection',
      comparedToYesterday: 'Par rapport à hier ({value}%) {change}',
      improve: 'améliorée',
      decrease: 'diminuée',
      rate: 'Précision'
    },
    alerts: {
      title: 'Alertes Récentes',
      new: 'Nouveau',
      noAlerts: 'Aucune alerte'
    },
    trend: {
      title: 'Tendance de Détection (7 Derniers Jours)',
      total: 'Total',
      pass: 'Réussite',
      fail: 'Échec'
    }
  },
  history: {
    searchText: 'Rechercher Texte',
    status: {
      title: 'Résultat de Détection',
      all: 'Tous',
      pass: 'Réussite',
      fail: 'Échec',
      unknown: 'Inconnu'
    },
    dateRange: 'Plage de Dates',
    search: 'Rechercher',
    export_excel: 'Exporter',
    noData: 'Aucun enregistrement historique',
    detail: {
      title: 'Détails de l\'Enregistrement de Détection',
      originalImage: 'Image Originale',
      processedImage: 'Image Traitée',
      noImage: 'Aucune Image',
      timestamp: 'Heure de Détection',
      status: 'Résultat de Détection',
      text: 'Texte Reconnu',
      noText: 'Impossible de Reconnaître',
      confidence: 'Confiance',
      device: 'Appareil Utilisé'
    },
    columns: {
      timestamp: 'Heure de Détection',
      text: 'Texte Reconnu',
      confidence: 'Confiance',
      status: 'Résultat de Détection',
      device: 'Appareil Utilisé',
      actions: 'Actions'
    },
    delete: {
      confirm: 'Êtes-vous sûr de vouloir supprimer cet enregistrement de détection ?'
    },
    export: {
      loading: 'Préparation de l\'exportation des données...',
      noData: 'Aucun enregistrement correspondant à exporter',
      success: 'Exportation réussie de {count} enregistrements',
      failed: 'Échec de l\'exportation',
      fileName: 'Historique de Détection',
      columns: {
        timestamp: 'Heure de Détection',
        text: 'Texte Reconnu',
        confidence: 'Confiance',
        status: 'Résultat de Détection',
        device: 'Appareil Utilisé',
        imageUrl: 'URL de l\'Image',
        processedImageUrl: 'URL de l\'Image Traitée'
      }
    }
  },
  annotation: {
    datasets: {
      title: 'Ensembles de Données',
      create: 'Nouvel Ensemble de Données',
      count: '{count} ensembles de données',
      imageCount: '{count} images'
    },
    selectDataset: 'Veuillez sélectionner un ensemble de données',
    selectImage: 'Veuillez sélectionner une image',
    selectImageHint: 'Sélectionnez une image dans la liste de gauche pour l\'annoter',
    actions: {
      deleteSelected: 'Supprimer la Sélection',
      upload: 'Télécharger des Images',
      rename: 'Renommer',
      gridView: 'Vue en Grille',
      annotationView: 'Vue d\'Annotation',
      export: 'Exporter l\'Ensemble de Données',
      import: 'Importer l\'Ensemble de Données',
      generate: 'Générer des Données',
      more: 'Plus',
      deleteDataset: 'Supprimer l\'Ensemble de Données'
    },
    dialogs: {
      upload: {
        title: 'Télécharger des Images',
        selectFiles: 'Sélectionner des Images',
        upload: 'Télécharger'
      },
      create: {
        title: 'Nouvel Ensemble de Données',
        name: 'Nom de l\'Ensemble de Données',
        nameRequired: 'Veuillez entrer le nom de l\'ensemble de données',
        type: 'Type d\'Ensemble de Données',
        create: 'Créer'
      },
      rename: {
        title: 'Renommer l\'Ensemble de Données',
        name: 'Nom de l\'Ensemble de Données',
        nameRequired: 'Veuillez entrer le nom de l\'ensemble de données'
      },
      delete: {
        title: 'Confirmer la Suppression',
        confirmImages: 'Êtes-vous sûr de vouloir supprimer {count} images sélectionnées ? Cette action ne peut pas être annulée.',
        confirmDataset: 'Êtes-vous sûr de vouloir supprimer l\'ensemble de données "{name}" ? Cette action ne peut pas être annulée.'
      }
    },
    datasetTypes: {
      textRegion: 'Ensemble de Données de Région de Texte',
      ocr: 'Ensemble de Données OCR'
    },
    notifications: {
      loadDatasetsFailed: 'Échec du chargement des ensembles de données, veuillez réessayer',
      createDatasetSuccess: 'Ensemble de données créé avec succès',
      createDatasetFailed: 'Échec de la création de l\'ensemble de données, veuillez réessayer',
      renameSuccess: 'Renommé avec succès',
      renameFailed: 'Échec du renommage, veuillez réessayer',
      deleteDatasetSuccess: 'Ensemble de données supprimé avec succès',
      deleteDatasetFailed: 'Échec de la suppression de l\'ensemble de données, veuillez réessayer',
      deleteImageSuccess: 'Image supprimée avec succès',
      deleteImageFailed: 'Échec de la suppression de l\'image, veuillez réessayer'
    }
  },
  annotator: {
    controls: {
      zoomIn: 'Zoom Avant',
      zoomOut: 'Zoom Arrière',
      save: 'Enregistrer les Annotations',
      reload: 'Recharger',
      deleteSelectedChar: 'Supprimer la Sélection ({char})',
      cancelDrawing: 'Annuler le Dessin',
      closeDetails: 'Fermer les Détails',
      enterFullscreen: 'Plein Écran',
      exitFullscreen: 'Quitter le Plein Écran',
      deleteSelected: 'Supprimer la Sélection'
    },
    tools: {
      textRegion: 'Région de Texte (Polygone)',
      character: 'Caractère (Rectangle)',
      wheelText: 'Texte Circulaire (Rectangle)'
    },
    ocr: {
      currentChar: 'Caractère Actuel',
      selectChar: 'Sélectionner le Caractère',
      commonChars: 'Caractères Communs',
      more: 'Plus',
      char: 'Caractère',
      position: 'Position',
      selectCharTitle: 'Sélectionner le Caractère d\'Annotation',
      inputChar: 'Saisir le Caractère',
      singleCharRequired: 'Veuillez entrer un seul caractère',
      commonCharSets: 'Ensembles de Caractères Communs',
      recentlyUsed: 'Récemment Utilisés',
      selectCharFirst: 'Veuillez d\'abord sélectionner un caractère'
    },
    preview: {
      toggleAnnotations: 'Afficher/Masquer les Annotations',
      toggleLabels: 'Afficher/Masquer les Étiquettes',
      label: 'Étiquette',
      position: 'Position',
      clickToViewDetails: 'Cliquer pour Voir les Détails',
      loading: 'Chargement...'
    },
    notifications: {
      loadFailed: 'Échec du chargement des annotations',
      saveSuccess: 'Annotations enregistrées avec succès',
      saveFailed: 'Échec de l\'enregistrement des annotations',
      deleteFailed: 'Échec de la suppression de l\'annotation'
    }
  },
  notFound: {
    message: 'Page Non Trouvée',
    backToHome: 'Retour à l\'Accueil'
  },
  generateData: {
    title: 'Générer des Données',
    sourceDataset: {
      title: 'Ensemble de Données Source',
      name: 'Nom de l\'Ensemble de Données',
      imageCount: '{count} Images',
      annotatedCount: '{count} Annotées'
    },
    targetDataset: {
      title: 'Ensemble de Données Cible',
      newOption: 'Créer un Nouvel Ensemble de Données',
      existingOption: 'Utiliser un Ensemble de Données Existant',
      sourceOption: 'Utiliser l\'Ensemble de Données Source',
      new: {
        name: {
          required: 'Veuillez entrer le nom de l\'ensemble de données'
        }
      },
      existing: {
        select: 'Veuillez sélectionner l\'ensemble de données cible'
      }
    },
    generateOptions: {
      title: 'Options de Génération',
      includeAnnotations: 'Inclure les Annotations',
      includeAnnotationsHint: 'Si coché, les annotations des images originales seront copiées'
    },
    operations: {
      title: 'Sélection d\'Opération',
      available: 'Opérations Disponibles',
      selected: 'Opérations Sélectionnées',
      configure: 'Configurer les Paramètres',
      duplicate: 'Dupliquer l\'Opération',
      remove: 'Supprimer l\'Opération',
      single: 'Unique',
      pipeline: 'Pipeline'
    },
    preview: {
      title: 'Aperçu',
      sourceImage: 'Image Source',
      imageId: 'ID: {id}',
      originalImage: 'Image Originale',
      operationResult: {
        single: 'Unique',
        pipeline: 'Pipeline'
      }
    },
    actions: {
      preview: 'Générer l\'Aperçu',
      generate: 'Démarrer la Génération'
    },
    progress: {
      title: 'Progression de la Génération',
      cancel: 'Annuler la Génération',
      close: 'Fermer'
    },
    configuration: {
      title: 'Configuration de {name}',
      sections: {
        input: 'Paramètres d\'Entrée',
        output: 'Paramètres de Sortie'
      },
      params: {
        required: 'Paramètre Obligatoire',
        optional: 'Paramètre Optionnel',
        defaultValue: 'Par défaut: {value}',
        yes: 'Oui',
        no: 'Non'
      },
      imageParam: {
        hint: 'Sélectionner la source d\'entrée d\'image',
        useDataset: 'Utiliser l\'Image de l\'Ensemble de Données',
        upload: 'Télécharger une Image Personnalisée'
      },
      annotationParam: {
        hint: 'Sélectionner la source de données d\'annotation',
        useDataset: 'Utiliser l\'Annotation de l\'Ensemble de Données',
        custom: 'Données d\'Annotation Personnalisées',
        customHint: 'Veuillez entrer des données d\'annotation au format JSON valide'
      },
      output: {
        hint: 'Sélectionner les résultats de sortie à enregistrer',
        image: {
          title: 'Sortie d\'Image',
          noOutput: 'Pas de sortie d\'image pour cette opération'
        },
        annotation: {
          title: 'Sortie d\'Annotation',
          noOutput: 'Pas de sortie d\'annotation pour cette opération'
        }
      },
      actions: {
        reset: 'Réinitialiser les Paramètres',
        close: 'Fermer'
      }
    },
    notifications: {
      loadError: 'Échec du chargement des données',
      previewError: 'Échec de la génération de l\'aperçu',
      generateSuccess: 'Génération de données terminée',
      generateError: 'Échec de la génération de données',
      cancelConfirm: {
        title: 'Confirmation d\'Annulation',
        message: 'Êtes-vous sûr de vouloir annuler la tâche de génération en cours ?',
        canceled: 'Tâche de génération annulée'
      }
    }
  },
  modelTester: {
    selectModel: {
      title: 'Veuillez Sélectionner un Modèle',
      hint: 'Sélectionnez un modèle entraîné dans la liste pour le tester'
    },
    model: {
      id: 'ID du Modèle'
    },
    params: {
      title: 'Paramètres',
      confThreshold: 'Seuil de Confiance',
      iouThreshold: 'Seuil IOU'
    },
    image: {
      title: 'Image de Test',
      select: 'Sélectionner une Image',
      test: 'Tester le Modèle'
    },
    result: {
      title: 'Résultats du Test',
      noImage: 'Veuillez télécharger une image à tester',
      preview: 'Aperçu de l\'Image',
      detectionResult: 'Résultat de Détection',
      detectedObjects: 'Objets Détectés:',
      confidence: 'Confiance',
      noDetection: 'Aucun objet détecté'
    },
    notifications: {
      noImageData: 'Échec de l\'obtention des données d\'image',
      noObjectsDetected: 'Aucun objet détecté',
      detectionCount: '{count} objets détectés',
      testFailed: 'Échec du test: {error}',
      testError: 'Erreur de test: {error}'
    }
  },
  alarmPanel: {
    title: {
      info: '',
      warning: 'Avertissement Système',
      error: 'Erreur Système',
      critical: 'Défaillance Grave',
      default: 'Alarme Système'
    },
    actions: {
      acknowledgeAll: 'Confirmer Tout',
      close: 'Fermer'
    },
    status: {
      alarmCount: '{count} alarmes au total',
      emergencyStop: 'Arrêt d\'Urgence'
    },
    notifications: {
      alarmAcknowledged: 'Alarme confirmée',
      allAlarmsAcknowledged: 'Toutes les alarmes confirmées'
    }
  },
  cameraPreview: {
    loading: 'Chargement de la caméra...',
    error: {
      connection: 'Impossible de se connecter à la caméra',
      status: 'Erreur lors de l\'obtention de l\'état de la caméra:'
    },
    stream: {
      alt: 'Vue de la caméra'
    }
  },
  model: {
    list: {
      title: 'Liste des Modèles',
      empty: 'Aucun modèle disponible',
      create: 'Créer un Modèle',
      refresh: 'Actualiser la Liste',
      architecture: 'Architecture du Modèle',
      actions: {
        test: 'Tester le Modèle',
        delete: 'Supprimer le Modèle'
      }
    },
    training: {
      title: 'Paramètres d\'Entraînement',
      params: {
        architecture: 'Architecture du Modèle',
        epochs: 'Époques d\'Entraînement',
        batchSize: 'Taille du Lot',
        imgSize: 'Taille de l\'Image',
        confThres: 'Seuil de Confiance',
        iouThres: 'Seuil IOU'
      },
      start: 'Démarrer l\'Entraînement',
      stop: 'Arrêter l\'Entraînement',
      modes: {
        config: 'Configurer l\'Entraînement',
        test: 'Tester le Modèle',
        logs: 'Journaux d\'Entraînement',
        files: 'Fichiers d\'Entraînement'
      },
      actions: {
        startTraining: 'Démarrer l\'Entraînement',
        stopTraining: 'Arrêter l\'Entraînement',
        testModel: 'Tester le Modèle',
        viewLogs: 'Voir les Journaux',
      }
    },
    progress: {
      title: 'Progression de l\'Entraînement',
      refresh: 'Actualiser la Progression',
      epoch: 'Époque Actuelle',
      loss: 'Valeur de Perte',
      eta: 'Temps Estimé Restant'
    },
    logs: {
      title: 'Journaux d\'Entraînement',
      refresh: 'Actualiser les Journaux',
      copy: 'Copier les Journaux',
      scrollToBottom: 'Défiler vers le Bas',
      empty: 'Aucun journal disponible'
    },
    files: {
      title: 'Fichiers du Modèle',
      refresh: 'Actualiser les Fichiers',
      root: 'Retour à la Racine',
      download: 'Télécharger le Fichier',
      preview: 'Aperçu du Fichier',
      empty: 'Aucun fichier disponible',
      actions: {
        root: 'Retour à la Racine',
      }
    },
    dialogs: {
      create: {
        title: 'Créer un Nouveau Modèle',
        name: 'Nom du Modèle',
        nameRequired: 'Veuillez entrer un nom de modèle',
        dataset: 'Ensemble de Données d\'Entraînement',
        datasetRequired: 'Veuillez sélectionner un ensemble de données d\'entraînement'
      },
      delete: {
        message: 'Êtes-vous sûr de vouloir supprimer le modèle {name} ? Cette action ne peut pas être annulée.'
      }
    },
    notifications: {
      createSuccess: 'Modèle créé avec succès',
      createFailed: 'Échec de la création du modèle: {error}',
      deleteSuccess: 'Modèle supprimé avec succès',
      deleteFailed: 'Échec de la suppression du modèle: {error}',
      trainStarted: 'Entraînement du modèle démarré',
      trainFailed: 'Échec du démarrage de l\'entraînement: {error}',
      updateParamsFailed: 'Échec de la mise à jour des paramètres: {error}',
      loadDatasetsFailed: 'Échec du chargement des ensembles de données',
      copyModelId: 'ID du modèle copié',
      copyModelIdFailed: 'Échec de la copie de l\'ID du modèle',
      copyLogs: 'Journaux copiés',
      copyLogsFailed: 'Échec de la copie des journaux',
      downloadStarted: 'Téléchargement de {name} démarré'
    },
    status: {
      empty: 'Veuillez sélectionner un modèle',
      emptyHint: 'Sélectionnez un modèle dans la liste à gauche, ou créez-en un nouveau',
      notTraining: 'Le modèle n\'est pas en cours d\'entraînement, aucun journal d\'entraînement disponible',
      notCompleted: 'Ce modèle n\'a pas terminé l\'entraînement et ne peut pas être testé',
      selectFeature: 'Veuillez sélectionner une fonctionnalité ou une opération'
    }
  },
  realtime: {
    title: 'Surveillance en Temps Réel',
    camera: {
      select: 'Sélectionner une Caméra',
      video: 'Vidéo de la Caméra',
      processed: 'Vidéo Traitée',
      processing: 'Traitement...',
      streamActive: 'Flux de Traitement Actif',
      streamWaiting: 'En Attente du Flux...'
    },
    operation: {
      title: 'Sélection d\'Opération',
      select: 'Sélectionner une Opération de Traitement d\'Image',
      selectRequired: 'Veuillez sélectionner une opération',
      types: {
        single: 'Unique',
        pipeline: 'Pipeline'
      },
      apply: 'Appliquer l\'Opération',
      startStream: 'Démarrer le Flux de Traitement',
      stopStream: 'Arrêter le Flux de Traitement',
      detection: 'Détection'
    },
    result: {
      title: 'Résultats de Détection',
      waiting: 'En attente des résultats de détection...',
      status: {
        pass: 'Succès',
        fail: 'Échec'
      },
      details: {
        time: 'Heure de Détection',
        source: 'Source d\'Image',
        text: 'Texte Reconnu',
        confidence: 'Confiance',
        error: 'Raison de l\'erreur',
        filename: 'Nom du fichier',
        noText: 'Impossible de reconnaître'
      }
    },
    control: {
      title: 'Contrôle de la caméra',
      autoDetect: {
        start: 'Démarrer la détection automatique',
        stop: 'Arrêter la détection automatique'
      },
      capture: 'Capture unique',
      exposure: 'Temps d\'exposition',
      gain: 'Gain'
    },
    notifications: {
      selectCamera: 'Veuillez d\'abord sélectionner une caméra',
      selectOperation: 'Veuillez d\'abord sélectionner une opération',
      cameraUnavailable: 'La caméra sélectionnée n\'est actuellement pas disponible',
      startProcessing: 'Démarrage du traitement vidéo...',
      invalidOperation: 'Informations d\'opération invalides',
      streamStarted: 'Traitement en temps réel démarré',
      streamStartFailed: 'Échec du démarrage du flux de traitement : {error}',
      stopProcessing: 'Arrêt du traitement vidéo...',
      streamStopped: 'Traitement en temps réel arrêté',
      streamError: 'Échec du chargement du flux de traitement, veuillez vérifier la caméra et la connexion réseau',
      retrying: 'Chargement du flux de traitement, nouvelle tentative...',
      streamConnected: 'Flux de traitement connecté',
      autoDetectStarted: 'Détection automatique démarrée',
      autoDetectStopped: 'Détection automatique arrêtée',
      processingComplete: 'Traitement d\'image terminé',
      processingFailed: 'Échec du traitement d\'image : {error}',
      uploadImage: 'Aucun flux de caméra actif, veuillez télécharger une image',
      noCameraControl: 'Contrôle de caméra introuvable',
      cameraSelected: 'Caméra sélectionnée : {name}'
    },
    status: {
      online: 'En ligne',
      offline: 'Hors ligne',
      error: 'Erreur',
      unknown: 'Inconnu'
    }
  },
  cvOperation: {
    tabs: {
      single: 'Opération unique',
      pipeline: 'Opération en pipeline'
    }
  },
  camera: {
    capture: {
      loading: 'Chargement de la caméra...',
      error: 'Échec du chargement du flux de traitement, veuillez vérifier la caméra et la connexion réseau',
      noCamera: 'Aucun flux de caméra actif, veuillez télécharger une image',
      uploadedImage: 'Image téléchargée, en attente de traitement',
      videoStream: 'Flux vidéo',
      streaming: 'En diffusion',
      stopped: 'Arrêté',
      useUploadedImage: 'Utiliser l\'image téléchargée',
      reupload: 'Retélécharger',
      capture: 'Capture',
      uploadImage: 'Télécharger une image',
      stopMonitoring: 'Arrêter la surveillance',
      startMonitoring: 'Démarrer la surveillance'
    }
  },
  cv: {
    parameter: {
      name: 'Nom du paramètre',
      nameRequired: 'Veuillez entrer le nom du paramètre',
      type: 'Type de paramètre',
      typeRequired: 'Veuillez sélectionner le type de paramètre',
      description: 'Description',
      defaultValue: 'Valeur par défaut',
      required: 'Paramètre requis'
    },
    operation: {
      new: 'Nouvelle opération',
      import: 'Importer',
      importTooltip: 'Importer la configuration de l\'opération',
      export: 'Exporter',
      exportTooltip: 'Exporter la configuration de l\'opération',
      delete: 'Supprimer',
      deleteSelected: 'Supprimer ({count})',
      deleteTooltip: 'Supprimer les opérations sélectionnées',
      operationCount: '{count} Opérations',
      search: 'Rechercher le nom ou la description de l\'opération',
      refresh: 'Actualiser la liste',
      columns: {
        name: 'Nom de l\'opération',
        description: 'Description',
        createdAt: 'Date de création',
        actions: 'Actions'
      },
      actions: {
        edit: 'Modifier',
        test: 'Tester',
        delete: 'Supprimer'
      },
      deleteConfirm: {
        title: 'Confirmation de suppression',
        singleMessage: 'Êtes-vous sûr de vouloir supprimer l\'opération "{name}" ?',
        batchMessage: 'Êtes-vous sûr de vouloir supprimer {count} opérations sélectionnées ?',
        cancel: 'Annuler',
        confirm: 'Supprimer'
      },
      validation: {
        nameRequired: 'Le nom de l\'opération ne peut pas être vide',
        invalidCode: 'Format de code invalide'
      },
      importExport: {
        importErrorDetails: 'Détails de l\'erreur d\'importation',
        exportColumns: {
          name: 'Nom de l\'opération',
          description: 'Description',
          code: 'Code',
          inputParams: 'Paramètres d\'entrée',
          outputParams: 'Paramètres de sortie',
          createdAt: 'Date de création',
          updatedAt: 'Date de mise à jour'
        },
        exportSheetName: 'Opérations',
        exportFileName: 'cv_operations'
      },
      notifications: {
        loadError: 'Échec du chargement des opérations',
        saveSuccess: 'Opération enregistrée avec succès',
        saveError: 'Échec de l\'enregistrement de l\'opération',
        deleteSuccess: 'Opération supprimée avec succès',
        batchDeleteSuccess: 'Opérations supprimées avec succès',
        deleteError: 'Échec de la suppression de l\'opération',
        importFailed: 'Échec de l\'importation de l\'opération "{name}"',
        importPartialSuccess: 'Importation terminée : {success} réussis, {failed} échoués',
        importSuccess: '{count} opérations importées avec succès',
        importError: 'Échec de l\'importation',
        exportSuccess: '{count} opérations exportées avec succès',
        exportError: 'Échec de l\'exportation'
      }
    },
    operationEditor: {
      title: {
        edit: 'Modifier l\'opération',
        new: 'Nouvelle opération'
      },
      actions: {
        test: 'Exécuter',
        save: 'Enregistrer',
        close: 'Fermer'
      },
      basicInfo: {
        title: 'Informations de base',
        name: 'Nom de l\'opération',
        nameRequired: 'Veuillez entrer le nom de l\'opération',
        description: 'Description'
      },
      parameters: {
        title: 'Configuration des paramètres',
        tabs: {
          input: 'Paramètres d\'entrée',
          output: 'Paramètres de sortie'
        },
        param: 'Paramètre {index}',
        addInput: 'Ajouter un paramètre d\'entrée',
        addOutput: 'Ajouter un paramètre de sortie'
      },
      codeEditor: {
        title: 'Éditeur de code Python'
      },
      notifications: {
        initError: 'Échec de l\'initialisation de l\'éditeur',
        extractError: 'Échec de l\'extraction du code utilisateur',
        updateError: 'Échec de la mise à jour du modèle de code',
        editorError: 'Échec de la récupération du contenu de l\'éditeur',
        setContentError: 'Échec de la définition du contenu de l\'éditeur'
      }
    },
    pipeline: {
      new: 'Nouveau pipeline',
      import: 'Importer',
      importTooltip: 'Importer la configuration du pipeline',
      export: 'Exporter',
      exportTooltip: 'Exporter la configuration du pipeline',
      delete: 'Supprimer',
      deleteSelected: 'Supprimer ({count})',
      deleteTooltip: 'Supprimer les pipelines sélectionnés',
      pipelineCount: '{count} Pipelines',
      nodeCount: '{count} Nœuds',
      search: 'Rechercher le nom ou la description du pipeline',
      refresh: 'Actualiser la liste',
      columns: {
        name: 'Nom du pipeline',
        description: 'Description',
        nodes: 'Nœuds',
        createdAt: 'Date de création',
        actions: 'Actions'
      },
      actions: {
        edit: 'Modifier',
        test: 'Tester',
        delete: 'Supprimer'
      },
      deleteConfirm: {
        title: 'Confirmation de suppression',
        singleMessage: 'Êtes-vous sûr de vouloir supprimer le pipeline "{name}" ?',
        batchMessage: 'Êtes-vous sûr de vouloir supprimer {count} pipelines sélectionnés ?',
        cancel: 'Annuler',
        confirm: 'Supprimer'
      },
      validation: {
        nameRequired: 'Le nom du pipeline ne peut pas être vide',
        metadataRequired: 'Les métadonnées du pipeline ne peuvent pas être vides',
        invalidMetadata: 'Configuration de pipeline invalide',
        fileSizeLimit: 'La taille du fichier ne peut pas dépasser 10 Mo',
        fileTypeError: 'Seuls les fichiers .xlsx sont pris en charge',
        missingField: 'Champ requis manquant : {field}'
      },
      importExport: {
        errorDetails: 'Détails de l\'erreur d\'importation',
        columns: {
          name: 'Nom du pipeline',
          description: 'Description',
          metadata: 'Métadonnées',
          inputParams: 'Paramètres d\'entrée',
          outputParams: 'Paramètres de sortie',
          createdAt: 'Date de création',
          updatedAt: 'Date de mise à jour'
        },
        sheetName: 'Pipelines',
        fileName: 'pipelines'
      },
      notifications: {
        loadError: 'Échec du chargement des pipelines',
        saveSuccess: 'Pipeline enregistré avec succès',
        saveError: 'Échec de l\'enregistrement du pipeline',
        deleteSuccess: 'Pipeline supprimé avec succès',
        batchDeleteSuccess: 'Pipelines supprimés avec succès',
        deleteError: 'Échec de la suppression du pipeline',
        importFailed: 'Échec de l\'importation du pipeline "{name}" : {error}',
        importPartialSuccess: 'Importation terminée : {success} réussis, {failed} échoués',
        importSuccess: '{count} pipelines importés avec succès',
        importError: 'Échec de l\'importation',
        exportSuccess: '{count} pipelines exportés avec succès',
        exportError: 'Échec de l\'exportation',
        testPanelError: 'Impossible d\'ouvrir le panneau de test : Le pipeline n\'existe pas',
        jsonParseError: 'Échec de l\'analyse du JSON'
      }
    },
    operationTestPanel: {
      title: 'Test d\'opération',
      actions: {
        run: 'Exécuter',
        close: 'Fermer'
      },
      input: {
        title: 'Paramètres d\'entrée',
        jsonFormat: ' (format JSON)'
      },
      output: {
        title: 'Résultats de sortie'
      },
      validation: {
        required: 'Champ requis',
        invalidJson: 'Veuillez entrer un format JSON valide'
      }
    },
    pipelineEditor: {
      title: {
        new: 'Nouveau pipeline',
        edit: 'Modifier le pipeline'
      },
      actions: {
        run: 'Exécuter',
        save: 'Enregistrer',
        close: 'Fermer'
      },
      basicInfo: {
        title: 'Informations de base',
        name: 'Nom du pipeline',
        nameRequired: 'Veuillez entrer le nom du pipeline',
        description: 'Description'
      },
      nodeToolbox: {
        title: 'Boîte à outils des nœuds'
      },
      nodeProperties: {
        title: 'Propriétés du nœud',
        name: 'Nom du nœud',
        operation: 'Sélectionner l\'opération',
        noOperationFound: 'Aucune opération correspondante trouvée',
        noDescription: 'Aucune description',
        parameters: {
          title: 'Configuration des paramètres',
          valueSource: 'Source de valeur',
          customValue: 'Valeur personnalisée',
          customValueJson: 'Valeur personnalisée (Format JSON)'
        }
      },
      flowEditor: {
        title: 'Concepteur de pipeline',
        undo: 'Annuler (Ctrl+Z)',
        redo: 'Rétablir (Ctrl+Y)',
        delete: 'Supprimer la sélection (Suppr)',
        clear: 'Effacer le canevas',
        center: 'Centrer la vue',
        zoomIn: 'Zoom avant',
        zoomOut: 'Zoom arrière'
      },
      notifications: {
        cannotDeleteStartEnd: 'Impossible de supprimer les nœuds de début et de fin',
        initFailed: 'Échec de l\'initialisation du concepteur de pipeline'
      }
    }
  }
} 
