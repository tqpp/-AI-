export default {
  common: {
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    add: 'Add',
    confirm: 'Confirm',
    minutes: 'Minutes',
    loading: 'Loading...',
    success: 'Success',
    error: 'Error',
    warning: 'Warning',
    info: 'Info',
    menu: 'Menu',
    systemName: 'AI demo HUB'
  },
  settings: {
    system: {
      title: 'System Configuration',
      language: 'System Language',
      autoSaveInterval: 'Auto Save Interval',
      dataRetention: 'Data Retention',
      alarmThreshold: 'Alarm Threshold'
    },
    mes: {
      title: 'MES Integration',
      serverUrl: 'Server Address',
      apiKey: 'API Key',
      testConnection: 'Test Connection'
    },
    devices: {
      title: 'Device Management',
      all: 'All',
      camera: 'Camera',
      light: 'Light',
      plc: 'Controller',
      disableAutoCheck: 'Disable Auto Check',
      refreshStatus: 'Refresh Device Status',
      addDevice: 'Add Device',
      status: {
        online: 'Online',
        offline: 'Offline',
        error: 'Error',
        unknown: 'Unknown'
      },
      preview: {
        setOnline: 'Set Online',
        setOffline: 'Set Offline',
        edit: 'Edit Device',
        delete: 'Delete Device',
        title: '{name} Preview',
        status: 'Camera Status',
        streamUrl: 'Stream URL',
        notConfigured: 'Not Configured'
      },
      form: {
        title: {
          add: 'Add Device',
          edit: 'Edit Device'
        },
        name: 'Device Name',
        type: 'Device Type',
        model: 'Device Model',
        config: 'Device Configuration',
        camera: {
          type: 'Camera Type',
          types: {
            local: 'Local Camera',
            ip: 'IP Camera',
            rtsp: 'RTSP Stream',
            http: 'HTTP Stream'
          },
          deviceId: 'Device ID',
          streamUrl: 'Camera URL'
        },
        light: {
          port: 'Serial Port',
          mode: 'Working Mode',
          modes: {
            continuous: 'Continuous',
            flash: 'Flash',
            trigger: 'Trigger'
          }
        },
        plc: {
          ip: 'IP地址',
          rack: 'Rack Number',
          slot: 'Slot Number'
        }
      },
      noDevices: 'No {type} devices',
      deleteConfirm: 'Are you sure you want to delete device "{name}"?',
      type: {
        camera: 'Camera',
        light: 'Light',
        plc: 'Controller'
      }
    },
    notifications: {
      savingSettings: 'Guardando configuración del sistema...',
      settingsSaved: 'Configuración del sistema guardada',
      savingFailed: 'Error al guardar la configuración del sistema',
      savingMes: 'Guardando configuración MES...',
      mesSaved: 'Configuración MES guardada',
      mesSavingFailed: 'Error al guardar la configuración MES',
      loadDevicesFailed: 'Error al cargar la lista de dispositivos',
      deviceUpdated: 'Dispositivo actualizado',
      deviceAdded: 'Dispositivo añadido',
      deviceDeleted: 'Dispositivo eliminado',
      deviceSaveFailed: 'Error al guardar el dispositivo',
      deviceDeleteFailed: 'Error al eliminar el dispositivo',
      cameraIdError: 'Error al obtener el ID de la cámara, por favor verifique la configuración',
      deviceStatusChanged: '{name} {status}',
      deviceStatusUpdateFailed: 'Error al actualizar el estado del dispositivo',
      loadSettingsFailed: 'Error al cargar la configuración del sistema',
      loadMesFailed: 'Error al cargar la configuración MES',
      languageChanged: 'Idioma cambiado'
    }
  },
  status: {
    cameraList: 'Lista de Cámaras',
    noCameras: 'No hay cámaras configuradas',
    camera: 'Cámara',
    modelList: 'Lista de Modelos',
    noModels: 'No hay modelos cargados',
    model: 'Modelo',
    deviceList: 'Lista de Dispositivos',
    noDevices: 'No hay dispositivos de control configurados',
    device: 'Dispositivo',
    online: 'En Línea',
    offline: 'Fuera de Línea',
    error: 'Error',
    connected: 'Conectado',
    disconnected: 'Desconectado',
    partiallyConnected: 'Parcialmente Conectado',
    loaded: 'Cargado',
    notLoaded: 'No Cargado'
  },
  emergencyStop: {
    title: 'Parada de Emergencia',
    message: '¿Confirmar ejecutar la operación de parada de emergencia? Esto detendrá todas las operaciones de los dispositivos.',
    confirm: 'Confirmar Parada',
    executed: 'Operación de parada de emergencia ejecutada'
  },
  routes: {
    dashboard: 'Panel de Control',
    realtime: 'Monitoreo en Tiempo Real',
    history: 'Historial',
    annotation: 'Anotación de Datos',
    model: 'Entrenamiento de Modelo',
    modelTest: 'Prueba de Modelo',
    cvOperations: 'Procesamiento de Imágenes',
    settings: 'Configuración',
    notFound: 'Página No Encontrada'
  },
  dashboard: {
    systemStatus: {
      title: 'Estado del Sistema',
      uptime: 'Tiempo de Actividad',
      memory: 'Memoria',
      disk: 'Disco',
      systemNormal: 'Sistema Normal',
      systemLoadHigh: 'Carga del Sistema Alta',
      systemResourceStress: 'Estrés de Recursos del Sistema',
      systemStatusError: 'Error de Estado del Sistema',
      days: 'DÍAS ',
      hours: 'HORAS ',
      minutes: 'MINUTOS ',
      seconds: 'SEGUNDOS ',
      unknown:'DESCONHECIDO'
    },
    deviceStatus: {
      title: 'Estado de Dispositivos',
      onlineRate: 'Tasa de Conexión',
      total: 'Total',
      online: 'En Línea',
      offline: 'Fuera de Línea',
      error: 'Error',
      cameras: 'Cámaras'
    },
    detectionStats: {
      title: 'Estadísticas de Detección de Hoy',
      comparedToYesterday: 'Comparado con ayer ({count}) {change}',
      increase: 'aumento',
      decrease: 'disminución'
    },
    defectStats: {
      title: 'Estadísticas de Defectos de Hoy',
      comparedToYesterday: 'Comparado con ayer ({count}) {change}',
      increase: 'aumento',
      decrease: 'disminución'
    },
    accuracy: {
      title: 'Precisión de Detección',
      comparedToYesterday: 'Comparado con ayer ({value}%) {change}',
      improve: 'mejorado',
      decrease: 'disminuido',
      rate: 'Precisión'
    },
    alerts: {
      title: 'Alertas Recientes',
      new: 'Nuevo',
      noAlerts: 'Sin alertas'
    },
    trend: {
      title: 'Tendencia de Detección (Últimos 7 Días)',
      total: 'Total',
      pass: 'Aprobado',
      fail: 'Fallido'
    }
  },
  history: {
    searchText: 'Buscar Texto',
    status: {
      title: 'Resultado de Detección',
      all: 'Todos',
      pass: 'Aprobado',
      fail: 'Fallido',
      unknown: 'Desconocido'
    },
    dateRange: 'Rango de Fechas',
    search: 'Buscar',
    export_excel: 'Exportar',
    noData: 'Sin registros históricos',
    detail: {
      title: 'Detalles del Registro de Detección',
      originalImage: 'Imagen Original',
      processedImage: 'Imagen Procesada',
      noImage: 'Sin Imagen',
      timestamp: 'Tiempo de Detección',
      status: 'Resultado de Detección',
      text: 'Texto Reconocido',
      noText: 'No se puede Reconocer',
      confidence: 'Confianza',
      device: 'Dispositivo Utilizado'
    },
    columns: {
      timestamp: 'Tiempo de Detección',
      text: 'Texto Reconocido',
      confidence: 'Confianza',
      status: 'Resultado de Detección',
      device: 'Dispositivo Utilizado',
      actions: 'Acciones'
    },
    delete: {
      confirm: '¿Está seguro de que desea eliminar este registro de detección?'
    },
    export: {
      loading: 'Preparando para exportar datos...',
      noData: 'No hay registros coincidentes para exportar',
      success: 'Se exportaron exitosamente {count} registros',
      failed: 'Error al exportar',
      fileName: 'Historial de Detección',
      columns: {
        timestamp: 'Tiempo de Detección',
        text: 'Texto Reconocido',
        confidence: 'Confianza',
        status: 'Resultado de Detección',
        device: 'Dispositivo Utilizado',
        imageUrl: 'URL de la Imagen',
        processedImageUrl: 'URL de la Imagen Procesada'
      }
    }
  },
  annotation: {
    datasets: {
      title: 'Conjuntos de Datos',
      create: 'Nuevo Conjunto de Datos',
      count: '{count} conjuntos de datos',
      imageCount: '{count} imágenes'
    },
    selectDataset: 'Por favor seleccione un conjunto de datos',
    selectImage: 'Por favor seleccione una imagen',
    selectImageHint: 'Seleccione una imagen de la lista izquierda para anotar',
    actions: {
      deleteSelected: 'Eliminar Seleccionados',
      upload: 'Subir Imágenes',
      rename: 'Renombrar',
      gridView: 'Vista en Cuadrícula',
      annotationView: 'Vista de Anotación',
      export: 'Exportar Conjunto de Datos',
      import: 'Importar Conjunto de Datos',
      generate: 'Generar Datos',
      more: 'Más',
      deleteDataset: 'Eliminar Conjunto de Datos'
    },
    dialogs: {
      upload: {
        title: 'Subir Imágenes',
        selectFiles: 'Seleccionar Imágenes',
        upload: 'Subir'
      },
      create: {
        title: 'Nuevo Conjunto de Datos',
        name: 'Nombre del Conjunto de Datos',
        nameRequired: 'Por favor ingrese el nombre del conjunto de datos',
        type: 'Tipo de Conjunto de Datos',
        create: 'Crear'
      },
      rename: {
        title: 'Renombrar Conjunto de Datos',
        name: 'Nombre del Conjunto de Datos',
        nameRequired: 'Por favor ingrese el nombre del conjunto de datos'
      },
      delete: {
        title: 'Confirmar Eliminación',
        confirmImages: '¿Está seguro de que desea eliminar {count} imágenes seleccionadas? Esta acción no se puede deshacer.',
        confirmDataset: '¿Está seguro de que desea eliminar el conjunto de datos "{name}"? Esta acción no se puede deshacer.'
      }
    },
    datasetTypes: {
      textRegion: 'Conjunto de Datos de Región de Texto',
      ocr: 'Conjunto de Datos OCR'
    },
    notifications: {
      loadDatasetsFailed: 'Error al cargar conjuntos de datos, por favor intente nuevamente',
      createDatasetSuccess: 'Conjunto de datos creado exitosamente',
      createDatasetFailed: 'Error al crear conjunto de datos, por favor intente nuevamente',
      renameSuccess: 'Renombrado exitosamente',
      renameFailed: 'Error al renombrar, por favor intente nuevamente',
      deleteDatasetSuccess: 'Conjunto de datos eliminado exitosamente',
      deleteDatasetFailed: 'Error al eliminar conjunto de datos, por favor intente nuevamente',
      deleteImageSuccess: 'Imagen eliminada exitosamente',
      deleteImageFailed: 'Error al eliminar imagen, por favor intente nuevamente'
    }
  },
  annotator: {
    controls: {
      zoomIn: 'Acercar',
      zoomOut: 'Alejar',
      save: 'Guardar Anotaciones',
      reload: 'Recargar',
      deleteSelectedChar: 'Eliminar Seleccionado ({char})',
      cancelDrawing: 'Cancelar Dibujo',
      closeDetails: 'Cerrar Detalles',
      enterFullscreen: 'Entrar en Pantalla Completa',
      exitFullscreen: 'Salir de Pantalla Completa',
      deleteSelected: 'Eliminar Seleccionado'
    },
    tools: {
      textRegion: 'Región de Texto (Polígono)',
      character: 'Carácter (Rectángulo)',
      wheelText: 'Texto de Rueda (Rectángulo)'
    },
    ocr: {
      currentChar: 'Carácter Actual',
      selectChar: 'Seleccionar Carácter',
      commonChars: 'Caracteres Comunes',
      more: 'Más',
      char: 'Carácter',
      position: 'Posición',
      selectCharTitle: 'Seleccionar Carácter de Anotación',
      inputChar: 'Ingresar Carácter',
      singleCharRequired: 'Por favor ingrese un solo carácter',
      commonCharSets: 'Conjuntos de Caracteres Comunes',
      recentlyUsed: 'Recientemente Usados',
      selectCharFirst: 'Por favor seleccione un carácter primero'
    },
    preview: {
      toggleAnnotations: 'Alternar Anotaciones',
      toggleLabels: 'Alternar Etiquetas',
      label: 'Etiqueta',
      position: 'Posición',
      clickToViewDetails: 'Haga clic para ver detalles',
      loading: 'Cargando...'
    },
    notifications: {
      loadFailed: 'Error al cargar anotaciones',
      saveSuccess: 'Anotaciones guardadas exitosamente',
      saveFailed: 'Error al guardar anotaciones',
      deleteFailed: 'Error al eliminar anotación'
    }
  },
  notFound: {
    message: 'Página No Encontrada',
    backToHome: 'Volver al Inicio'
  },
  generateData: {
    title: 'Generar Datos',
    sourceDataset: {
      title: 'Conjunto de Datos Fuente',
      name: 'Nombre del Conjunto de Datos',
      imageCount: '{count} Imágenes',
      annotatedCount: '{count} Anotadas'
    },
    targetDataset: {
      title: 'Conjunto de Datos Destino',
      newOption: 'Crear Nuevo Conjunto de Datos',
      existingOption: 'Usar Conjunto de Datos Existente',
      sourceOption: 'Usar Conjunto de Datos Fuente',
      new: {
        name: {
          required: 'Por favor ingrese el nombre del conjunto de datos'
        }
      },
      existing: {
        select: 'Por favor seleccione el conjunto de datos destino'
      }
    },
    generateOptions: {
      title: 'Opciones de Generación',
      includeAnnotations: 'Incluir Anotaciones',
      includeAnnotationsHint: 'Si está marcado, se copiarán las anotaciones de las imágenes originales'
    },
    operations: {
      title: 'Selección de Operaciones',
      available: 'Operaciones Disponibles',
      selected: 'Operaciones Seleccionadas',
      configure: 'Configurar Parámetros',
      duplicate: 'Duplicar Operación',
      remove: 'Eliminar Operación',
      single: 'Único',
      pipeline: 'Canalización'
    },
    preview: {
      title: 'Vista Previa',
      sourceImage: 'Imagen Fuente',
      imageId: 'ID: {id}',
      originalImage: 'Imagen Original',
      operationResult: {
        single: 'Único',
        pipeline: 'Canalización'
      }
    },
    actions: {
      preview: 'Generar Vista Previa',
      generate: 'Iniciar Generación'
    },
    progress: {
      title: 'Progreso de Generación',
      cancel: 'Cancelar Generación',
      close: 'Cerrar'
    },
    configuration: {
      title: 'Configuración de {name}',
      sections: {
        input: 'Parámetros de Entrada',
        output: 'Parámetros de Salida'
      },
      params: {
        required: 'Parámetro Requerido',
        optional: 'Parámetro Opcional',
        defaultValue: 'Valor por Defecto: {value}',
        yes: 'Sí',
        no: 'No'
      },
      imageParam: {
        hint: 'Seleccionar fuente de entrada de imagen',
        useDataset: 'Usar Imagen del Conjunto de Datos',
        upload: 'Subir Imagen Personalizada'
      },
      annotationParam: {
        hint: 'Seleccionar fuente de datos de anotación',
        useDataset: 'Usar Anotación del Conjunto de Datos',
        custom: 'Datos de Anotación Personalizados',
        customHint: 'Por favor ingrese datos de anotación en formato JSON válido'
      },
      output: {
        hint: 'Seleccionar resultados de salida para guardar',
        image: {
          title: 'Salida de Imagen',
          noOutput: 'No hay salida de imagen para esta operación'
        },
        annotation: {
          title: 'Salida de Anotación',
          noOutput: 'No hay salida de anotación para esta operación'
        }
      },
      actions: {
        reset: 'Restablecer Parámetros',
        close: 'Cerrar'
      }
    },
    notifications: {
      loadError: 'Error al cargar datos',
      previewError: 'Error al generar vista previa',
      generateSuccess: 'Generación de datos completada',
      generateError: 'Error al generar datos',
      cancelConfirm: {
        title: 'Confirmar Cancelación',
        message: '¿Está seguro de que desea cancelar la tarea de generación actual?',
        canceled: 'Tarea de generación cancelada'
      }
    }
  },
  modelTester: {
    selectModel: {
      title: 'Por favor seleccione un modelo',
      hint: 'Seleccione un modelo entrenado de la lista para probar'
    },
    model: {
      id: 'ID del Modelo'
    },
    params: {
      title: 'Configuración de Parámetros',
      confThreshold: 'Umbral de Confianza',
      iouThreshold: 'Umbral IOU'
    },
    image: {
      title: 'Imagen de Prueba',
      select: 'Seleccionar Imagen',
      test: 'Probar Modelo'
    },
    result: {
      title: 'Resultados de Prueba',
      noImage: 'Por favor suba una imagen para probar',
      preview: 'Vista Previa de Imagen',
      detectionResult: 'Resultado de Detección',
      detectedObjects: 'Objetos Detectados:',
      confidence: 'Confianza',
      noDetection: 'No se detectaron objetos'
    },
    notifications: {
      noImageData: 'Error al obtener datos de imagen',
      noObjectsDetected: 'No se detectaron objetos',
      detectionCount: '{count} objetos detectados',
      testFailed: 'Error en la prueba: {error}',
      testError: 'Error de prueba: {error}'
    }
  },
  alarmPanel: {
    title: {
      info: '',
      warning: 'Advertencia del Sistema',
      error: 'Error del Sistema',
      critical: 'Falla Crítica',
      default: 'Alerta del Sistema'
    },
    actions: {
      acknowledgeAll: 'Confirmar Todo',
      close: 'Cerrar'
    },
    status: {
      alarmCount: 'Total {count} alertas',
      emergencyStop: 'Parada de Emergencia'
    },
    notifications: {
      alarmAcknowledged: 'Alerta confirmada',
      allAlarmsAcknowledged: 'Todas las alertas confirmadas'
    }
  },
  cameraPreview: {
    loading: 'Cargando cámara...',
    error: {
      connection: 'No se puede conectar a la cámara',
      status: 'Error al obtener estado de la cámara:'
    },
    stream: {
      alt: 'Vista de la cámara'
    }
  },
  model: {
    list: {
      title: 'Lista de Modelos',
      empty: 'No hay modelos disponibles',
      create: 'Crear Modelo',
      refresh: 'Actualizar Lista',
      architecture: 'Arquitectura del Modelo',
      actions: {
        test: 'Probar Modelo',
        delete: 'Eliminar Modelo'
      }
    },
    training: {
      title: 'Parámetros de Entrenamiento',
      params: {
        architecture: 'Arquitectura del Modelo',
        epochs: 'Épocas de Entrenamiento',
        batchSize: 'Tamaño del Lote',
        imgSize: 'Tamaño de Imagen',
        confThres: 'Umbral de Confianza',
        iouThres: 'Umbral IOU'
      },
      start: 'Iniciar Entrenamiento',
      stop: 'Detener Entrenamiento',
      modes: {
        config: 'Configurar Entrenamiento',
        test: 'Probar Modelo',
        logs: 'Registros de Entrenamiento',
        files: 'Archivos de Entrenamiento'
      },
      actions: {
        startTraining: 'Iniciar Entrenamiento',
        stopTraining: 'Detener Entrenamiento',
        testModel: 'Probar Modelo',
        viewLogs: 'Ver Registros',
      }
    },
    progress: {
      title: 'Progreso del Entrenamiento',
      refresh: 'Actualizar Progreso',
      epoch: 'Época Actual',
      loss: 'Valor de Pérdida',
      eta: 'Tiempo Estimado Restante'
    },
    logs: {
      title: 'Registros de Entrenamiento',
      refresh: 'Actualizar Registros',
      copy: 'Copiar Registros',
      scrollToBottom: 'Desplazar al Final',
      empty: 'No hay registros disponibles'
    },
    files: {
      title: 'Archivos del Modelo',
      refresh: 'Actualizar Archivos',
      root: 'Volver a la Raíz',
      download: 'Descargar Archivo',
      preview: 'Vista Previa del Archivo',
      empty: 'No hay archivos disponibles',
      actions: {
        root: 'Volver a la Raíz',
      }
    },
    dialogs: {
      create: {
        title: 'Crear Nuevo Modelo',
        name: 'Nombre del Modelo',
        nameRequired: 'Por favor ingrese un nombre para el modelo',
        dataset: 'Conjunto de Datos de Entrenamiento',
        datasetRequired: 'Por favor seleccione un conjunto de datos de entrenamiento'
      },
      delete: {
        message: '¿Está seguro de que desea eliminar el modelo {name}? Esta acción no se puede deshacer.'
      }
    },
    notifications: {
      createSuccess: 'Modelo creado exitosamente',
      createFailed: 'Error al crear modelo: {error}',
      deleteSuccess: 'Modelo eliminado exitosamente',
      deleteFailed: 'Error al eliminar modelo: {error}',
      trainStarted: 'Entrenamiento del modelo iniciado',
      trainFailed: 'Error al iniciar entrenamiento: {error}',
      updateParamsFailed: 'Error al actualizar parámetros: {error}',
      loadDatasetsFailed: 'Error al cargar conjuntos de datos',
      copyModelId: 'ID del modelo copiado',
      copyModelIdFailed: 'Error al copiar ID del modelo',
      copyLogs: 'Registros copiados',
      copyLogsFailed: 'Error al copiar registros',
      downloadStarted: 'Iniciada descarga de {name}'
    },
    status: {
      empty: 'Por favor seleccione un modelo',
      emptyHint: 'Seleccione un modelo de la lista a la izquierda, o cree uno nuevo',
      notTraining: 'El modelo no está entrenando actualmente, no hay registros de entrenamiento disponibles',
      notCompleted: 'Este modelo no ha completado el entrenamiento y no puede ser probado',
      selectFeature: 'Por favor seleccione una característica u operación'
    }
  },
  realtime: {
    title: 'Monitoreo en Tiempo Real',
    camera: {
      select: 'Seleccionar Cámara',
      video: 'Video de Cámara',
      processed: 'Video Procesado',
      processing: 'Procesando...',
      streamActive: 'Flujo de Procesamiento Activo',
      streamWaiting: 'Esperando Flujo...'
    },
    operation: {
      title: 'Selección de Operación',
      select: 'Seleccionar Operación de Procesamiento de Imagen',
      selectRequired: 'Por favor seleccione una operación',
      types: {
        single: 'Único',
        pipeline: 'Canalización'
      },
      apply: 'Aplicar Operación',
      startStream: 'Iniciar Flujo de Procesamiento',
      stopStream: 'Detener Flujo de Procesamiento',
      detection: 'Detección'
    },
    result: {
      title: 'Resultados de Detección',
      waiting: 'Esperando resultados de detección...',
      status: {
        pass: 'Aprobado',
        fail: 'Fallido'
      },
      details: {
        time: 'Tiempo de Detección',
        source: 'Fuente de Imagen',
        text: 'Texto Reconocido',
        confidence: 'Confianza',
        error: 'Razón del Error',
        filename: 'Nombre de Archivo',
        noText: 'No se puede reconocer'
      }
    },
    control: {
      title: 'Control de Cámara',
      autoDetect: {
        start: 'Iniciar Detección Automática',
        stop: 'Detener Detección Automática'
      },
      capture: 'Captura Única',
      exposure: 'Tiempo de Exposición',
      gain: 'Ganancia'
    },
    notifications: {
      selectCamera: 'Por favor seleccione una cámara primero',
      selectOperation: 'Por favor seleccione una operación primero',
      cameraUnavailable: 'La cámara seleccionada no está disponible actualmente',
      startProcessing: 'Iniciando procesamiento de video...',
      invalidOperation: 'Información de operación inválida',
      streamStarted: 'Procesamiento en tiempo real iniciado',
      streamStartFailed: 'Error al iniciar el flujo de procesamiento: {error}',
      stopProcessing: 'Deteniendo procesamiento de video...',
      streamStopped: 'Procesamiento en tiempo real detenido',
      streamError: 'Error al cargar el flujo de procesamiento, por favor verifique la cámara y la conexión de red',
      retrying: 'Cargando flujo de procesamiento, reintentando...',
      streamConnected: 'Flujo de procesamiento conectado',
      autoDetectStarted: 'Detección automática iniciada',
      autoDetectStopped: 'Detección automática detenida',
      processingComplete: 'Procesamiento de imagen completado',
      processingFailed: 'Error al procesar la imagen: {error}',
      uploadImage: 'No hay flujo de cámara activo, por favor suba una imagen',
      noCameraControl: 'Control de cámara no encontrado',
      cameraSelected: 'Cámara seleccionada: {name}'
    },
    status: {
      online: 'En línea',
      offline: 'Desconectado',
      error: 'Error',
      unknown: 'Desconocido'
    }
  },
  cvOperation: {
    tabs: {
      single: 'Operación Única',
      pipeline: 'Operación de Canalización'
    }
  },
  camera: {
    capture: {
      loading: 'Cargando cámara...',
      error: 'Error al cargar el flujo de procesamiento, por favor verifique la cámara y la conexión de red',
      noCamera: 'No hay flujo de cámara activo, por favor suba una imagen',
      uploadedImage: 'Imagen subida, esperando procesamiento',
      videoStream: 'Flujo de Video',
      streaming: 'Transmitiendo',
      stopped: 'Detenido',
      useUploadedImage: 'Usar imagen subida',
      reupload: 'Volver a subir',
      capture: 'Capturar',
      uploadImage: 'Subir Imagen',
      stopMonitoring: 'Detener Monitoreo',
      startMonitoring: 'Iniciar Monitoreo'
    }
  },
  cv: {
    parameter: {
      name: 'Nombre del Parámetro',
      nameRequired: 'Por favor ingrese el nombre del parámetro',
      type: 'Tipo de Parámetro',
      typeRequired: 'Por favor seleccione el tipo de parámetro',
      description: 'Descripción',
      defaultValue: 'Valor Predeterminado',
      required: 'Parámetro Requerido'
    },
    operation: {
      new: 'Nueva Operación',
      import: 'Importar',
      importTooltip: 'Importar configuración de operación',
      export: 'Exportar',
      exportTooltip: 'Exportar configuración de operación',
      delete: 'Eliminar',
      deleteSelected: 'Eliminar ({count})',
      deleteTooltip: 'Eliminar operaciones seleccionadas',
      operationCount: '{count} Operaciones',
      search: 'Buscar nombre o descripción de operación',
      refresh: 'Actualizar Lista',
      columns: {
        name: 'Nombre de Operación',
        description: 'Descripción',
        createdAt: 'Creado En',
        actions: 'Acciones'
      },
      actions: {
        edit: 'Editar',
        test: 'Probar',
        delete: 'Eliminar'
      },
      deleteConfirm: {
        title: 'Confirmar Eliminación',
        singleMessage: '¿Está seguro de que desea eliminar la operación "{name}"?',
        batchMessage: '¿Está seguro de que desea eliminar {count} operaciones seleccionadas?',
        cancel: 'Cancelar',
        confirm: 'Eliminar'
      },
      validation: {
        nameRequired: 'El nombre de la operación no puede estar vacío',
        invalidCode: 'Formato de código inválido'
      },
      importExport: {
        importErrorDetails: 'Detalles del Error de Importación',
        exportColumns: {
          name: 'Nombre de Operación',
          description: 'Descripción',
          code: 'Código',
          inputParams: 'Parámetros de Entrada',
          outputParams: 'Parámetros de Salida',
          createdAt: 'Creado En',
          updatedAt: 'Actualizado En'
        },
        exportSheetName: 'Operaciones',
        exportFileName: 'operaciones_cv'
      },
      notifications: {
        loadError: 'Error al cargar operaciones',
        saveSuccess: 'Operación guardada exitosamente',
        saveError: 'Error al guardar operación',
        deleteSuccess: 'Operación eliminada exitosamente',
        batchDeleteSuccess: 'Operaciones eliminadas exitosamente',
        deleteError: 'Error al eliminar operación',
        importFailed: 'Error al importar operación "{name}"',
        importPartialSuccess: 'Importación completada: {success} exitosos, {failed} fallidos',
        importSuccess: 'Se importaron exitosamente {count} operaciones',
        importError: 'Error en la importación',
        exportSuccess: 'Se exportaron exitosamente {count} operaciones',
        exportError: 'Error en la exportación'
      }
    },
    operationEditor: {
      title: {
        edit: 'Editar Operación',
        new: 'Nueva Operación'
      },
      actions: {
        test: 'Ejecutar',
        save: 'Guardar',
        close: 'Cerrar'
      },
      basicInfo: {
        title: 'Información Básica',
        name: 'Nombre de Operación',
        nameRequired: 'Por favor ingrese el nombre de la operación',
        description: 'Descripción'
      },
      parameters: {
        title: 'Configuración de Parámetros',
        tabs: {
          input: 'Parámetros de Entrada',
          output: 'Parámetros de Salida'
        },
        param: 'Parámetro {index}',
        addInput: 'Agregar Parámetro de Entrada',
        addOutput: 'Agregar Parámetro de Salida'
      },
      codeEditor: {
        title: 'Editor de Código Python'
      },
      notifications: {
        initError: 'Error al inicializar el editor',
        extractError: 'Error al extraer el código del usuario',
        updateError: 'Error al actualizar la plantilla de código',
        editorError: 'Error al obtener el contenido del editor',
        setContentError: 'Error al establecer el contenido del editor'
      }
    },
    pipeline: {
      new: 'Nueva Canalización',
      import: 'Importar',
      importTooltip: 'Importar configuración de canalización',
      export: 'Exportar',
      exportTooltip: 'Exportar configuración de canalización',
      delete: 'Eliminar',
      deleteSelected: 'Eliminar ({count})',
      deleteTooltip: 'Eliminar canalizaciones seleccionadas',
      pipelineCount: '{count} Canalizaciones',
      nodeCount: '{count} Nodos',
      search: 'Buscar nombre o descripción de canalización',
      refresh: 'Actualizar Lista',
      columns: {
        name: 'Nombre de Canalización',
        description: 'Descripción',
        nodes: 'Nodos',
        createdAt: 'Creado En',
        actions: 'Acciones'
      },
      actions: {
        edit: 'Editar',
        test: 'Probar',
        delete: 'Eliminar'
      },
      deleteConfirm: {
        title: 'Confirmar Eliminación',
        singleMessage: '¿Está seguro de que desea eliminar la canalización "{name}"?',
        batchMessage: '¿Está seguro de que desea eliminar {count} canalizaciones seleccionadas?',
        cancel: 'Cancelar',
        confirm: 'Eliminar'
      },
      validation: {
        nameRequired: 'El nombre de la canalización no puede estar vacío',
        metadataRequired: 'Los metadatos de la canalización no pueden estar vacíos',
        invalidMetadata: 'Configuración de canalización inválida',
        fileSizeLimit: 'El tamaño del archivo no puede exceder 10MB',
        fileTypeError: 'Solo se admiten archivos .xlsx',
        missingField: 'Campo requerido faltante: {field}'
      },
      importExport: {
        errorDetails: 'Detalles del Error de Importación',
        columns: {
          name: 'Nombre de Canalización',
          description: 'Descripción',
          metadata: 'Metadatos',
          inputParams: 'Parámetros de Entrada',
          outputParams: 'Parámetros de Salida',
          createdAt: 'Creado En',
          updatedAt: 'Actualizado En'
        },
        sheetName: 'Canalizaciones',
        fileName: 'canalizaciones'
      },
      notifications: {
        loadError: 'Error al cargar canalizaciones',
        saveSuccess: 'Canalización guardada exitosamente',
        saveError: 'Error al guardar canalización',
        deleteSuccess: 'Canalización eliminada exitosamente',
        batchDeleteSuccess: 'Canalizaciones eliminadas exitosamente',
        deleteError: 'Error al eliminar canalización',
        importFailed: 'Error al importar canalización "{name}": {error}',
        importPartialSuccess: 'Importación completada: {success} exitosos, {failed} fallidos',
        importSuccess: 'Se importaron exitosamente {count} canalizaciones',
        importError: 'Error en la importación',
        exportSuccess: 'Se exportaron exitosamente {count} canalizaciones',
        exportError: 'Error al exportar',
        testPanelError: 'No se puede abrir el panel de prueba: La canalización no existe',
        jsonParseError: 'Error al analizar JSON'
      }
    },
    operationTestPanel: {
      title: 'Prueba de Operación',
      actions: {
        run: 'Ejecutar',
        close: 'Cerrar'
      },
      input: {
        title: 'Parámetros de Entrada',
        jsonFormat: ' (formato JSON)'
      },
      output: {
        title: 'Resultados de Salida'
      },
      validation: {
        required: 'Campo requerido',
        invalidJson: 'Por favor ingrese un formato JSON válido'
      }
    },
    pipelineEditor: {
      title: {
        new: 'Nueva Canalización',
        edit: 'Editar Canalización'
      },
      actions: {
        run: 'Ejecutar',
        save: 'Guardar',
        close: 'Cerrar'
      },
      basicInfo: {
        title: 'Información Básica',
        name: 'Nombre de Canalización',
        nameRequired: 'Por favor ingrese el nombre de la canalización',
        description: 'Descripción'
      },
      nodeToolbox: {
        title: 'Caja de Herramientas de Nodos'
      },
      nodeProperties: {
        title: 'Propiedades del Nodo',
        name: 'Nombre del Nodo',
        operation: 'Seleccionar Operación',
        noOperationFound: 'No se encontró operación coincidente',
        noDescription: 'Sin descripción',
        parameters: {
          title: 'Configuración de Parámetros',
          valueSource: 'Fuente de Valor',
          customValue: 'Valor Personalizado',
          customValueJson: 'Valor Personalizado (Formato JSON)'
        }
      },
      flowEditor: {
        title: 'Diseñador de Canalización',
        undo: 'Deshacer (Ctrl+Z)',
        redo: 'Rehacer (Ctrl+Y)',
        delete: 'Eliminar Seleccionado (Supr)',
        clear: 'Limpiar Lienzo',
        center: 'Centrar Vista',
        zoomIn: 'Acercar',
        zoomOut: 'Alejar'
      },
      notifications: {
        cannotDeleteStartEnd: 'No se pueden eliminar los nodos de inicio y fin',
        initFailed: 'Error al inicializar el diseñador de canalización'
      }
    }
  }
} 
