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
      savingSettings: 'Saving system settings...',
      settingsSaved: 'System settings saved',
      savingFailed: 'Failed to save system settings',
      savingMes: 'Saving MES settings...',
      mesSaved: 'MES settings saved',
      mesSavingFailed: 'Failed to save MES settings',
      loadDevicesFailed: 'Failed to load device list',
      deviceUpdated: 'Device updated',
      deviceAdded: 'Device added',
      deviceDeleted: 'Device deleted',
      deviceSaveFailed: 'Failed to save device',
      deviceDeleteFailed: 'Failed to delete device',
      cameraIdError: 'Failed to get camera ID, please check the configuration',
      deviceStatusChanged: '{name} {status}',
      deviceStatusUpdateFailed: 'Failed to update device status',
      loadSettingsFailed: 'Failed to load system settings',
      loadMesFailed: 'Failed to load MES settings',
      languageChanged: 'Language changed'
    }
  },
  status: {
    cameraList: 'Camera List',
    noCameras: 'No cameras configured',
    camera: 'Camera',
    modelList: 'Model List',
    noModels: 'No models loaded',
    model: 'Model',
    deviceList: 'Device List',
    noDevices: 'No control devices configured',
    device: 'Device',
    online: 'Online',
    offline: 'Offline',
    error: 'Error',
    connected: 'Connected',
    disconnected: 'Disconnected',
    partiallyConnected: 'Partially Connected',
    loaded: 'Loaded',
    notLoaded: 'Not Loaded'
  },
  emergencyStop: {
    title: 'Emergency Stop',
    message: 'Confirm to execute emergency stop operation? This will stop all device operations.',
    confirm: 'Confirm Stop',
    executed: 'Emergency stop operation executed'
  },
  routes: {
    dashboard: 'Dashboard',
    realtime: 'Realtime Monitoring',
    history: 'History',
    annotation: 'Data Annotation',
    model: 'Model Training',
    modelTest: 'Model Test',
    cvOperations: 'Image Processing',
    settings: 'Settings',
    notFound: 'Page Not Found'
  },
  dashboard: {
    systemStatus: {
      title: 'System Status',
      uptime: 'Uptime',
      memory: 'Memory',
      disk: 'Disk',
      systemNormal: 'System Normal',
      systemLoadHigh: 'System Load High',
      systemResourceStress: 'System Resource Stress',
      systemStatusError: 'System Status Error',
      days: 'DAYS ',
      hours: 'HOURS ',
      minutes: 'MINUTES ',
      seconds: 'SECONDS ',
      unknown:'UNKNOWN'
    },
    deviceStatus: {
      title: 'Device Status',
      onlineRate: 'Online Rate',
      total: 'Total',
      online: 'Online',
      offline: 'Offline',
      error: 'Error',
      cameras: 'Cameras'
    },
    detectionStats: {
      title: 'Today\'s Detection Stats',
      comparedToYesterday: 'Compared to yesterday ({count}) {change}',
      increase: 'increase',
      decrease: 'decrease'
    },
    defectStats: {
      title: 'Today\'s Defect Stats',
      comparedToYesterday: 'Compared to yesterday ({count}) {change}',
      increase: 'increase',
      decrease: 'decrease'
    },
    accuracy: {
      title: 'Detection Accuracy',
      comparedToYesterday: 'Compared to yesterday ({value}%) {change}',
      improve: 'improved',
      decrease: 'decreased',
      rate: 'Accuracy'
    },
    alerts: {
      title: 'Recent Alerts',
      new: 'New',
      noAlerts: 'No alerts'
    },
    trend: {
      title: 'Detection Trend (Last 7 Days)',
      total: 'Total',
      pass: 'Pass',
      fail: 'Fail'
    }
  },
  history: {
    searchText: 'Search Text',
    status: {
      title: 'Detection Result',
      all: 'All',
      pass: 'Pass',
      fail: 'Fail',
      unknown: 'Unknown'
    },
    dateRange: 'Date Range',
    search: 'Search',
    export_excel: 'Export',
    noData: 'No historical records',
    detail: {
      title: 'Detection Record Details',
      originalImage: 'Original Image',
      processedImage: 'Processed Image',
      noImage: 'No Image',
      timestamp: 'Detection Time',
      status: 'Detection Result',
      text: 'Recognized Text',
      noText: 'Unable to Recognize',
      confidence: 'Confidence',
      device: 'Device Used'
    },
    columns: {
      timestamp: 'Detection Time',
      text: 'Recognized Text',
      confidence: 'Confidence',
      status: 'Detection Result',
      device: 'Device Used',
      actions: 'Actions'
    },
    delete: {
      confirm: 'Are you sure you want to delete this detection record?'
    },
    export: {
      loading: 'Preparing to export data...',
      noData: 'No matching records to export',
      success: 'Successfully exported {count} records',
      failed: 'Export failed',
      fileName: 'Detection History',
      columns: {
        timestamp: 'Detection Time',
        text: 'Recognized Text',
        confidence: 'Confidence',
        status: 'Detection Result',
        device: 'Device Used',
        imageUrl: 'Image URL',
        processedImageUrl: 'Processed Image URL'
      }
    }
  },
  annotation: {
    datasets: {
      title: 'Datasets',
      create: 'New Dataset',
      count: '{count} datasets',
      imageCount: '{count} images'
    },
    selectDataset: 'Please select a dataset',
    selectImage: 'Please select an image',
    selectImageHint: 'Select an image from the left list to annotate',
    actions: {
      deleteSelected: 'Delete Selected',
      upload: 'Upload Images',
      rename: 'Rename',
      gridView: 'Grid View',
      annotationView: 'Annotation View',
      export: 'Export Dataset',
      import: 'Import Dataset',
      generate: 'Generate Data',
      more: 'More',
      deleteDataset: 'Delete Dataset'
    },
    dialogs: {
      upload: {
        title: 'Upload Images',
        selectFiles: 'Select Images',
        upload: 'Upload'
      },
      create: {
        title: 'New Dataset',
        name: 'Dataset Name',
        nameRequired: 'Please enter dataset name',
        type: 'Dataset Type',
        create: 'Create'
      },
      rename: {
        title: 'Rename Dataset',
        name: 'Dataset Name',
        nameRequired: 'Please enter dataset name'
      },
      delete: {
        title: 'Confirm Delete',
        confirmImages: 'Are you sure you want to delete {count} selected images? This action cannot be undone.',
        confirmDataset: 'Are you sure you want to delete dataset "{name}"? This action cannot be undone.'
      }
    },
    datasetTypes: {
      textRegion: 'Text Region Dataset',
      ocr: 'OCR Dataset'
    },
    notifications: {
      loadDatasetsFailed: 'Failed to load datasets, please try again',
      createDatasetSuccess: 'Dataset created successfully',
      createDatasetFailed: 'Failed to create dataset, please try again',
      renameSuccess: 'Renamed successfully',
      renameFailed: 'Failed to rename, please try again',
      deleteDatasetSuccess: 'Dataset deleted successfully',
      deleteDatasetFailed: 'Failed to delete dataset, please try again',
      deleteImageSuccess: 'Image deleted successfully',
      deleteImageFailed: 'Failed to delete image, please try again'
    }
  },
  annotator: {
    controls: {
      zoomIn: 'Zoom In',
      zoomOut: 'Zoom Out',
      save: 'Save Annotations',
      reload: 'Reload',
      deleteSelectedChar: 'Delete Selected ({char})',
      cancelDrawing: 'Cancel Drawing',
      closeDetails: 'Close Details',
      enterFullscreen: 'Enter Fullscreen',
      exitFullscreen: 'Exit Fullscreen',
      deleteSelected: 'Delete Selected'
    },
    tools: {
      textRegion: 'Text Region (Polygon)',
      character: 'Character (Rectangle)',
      wheelText: 'Wheel Text (Rectangle)'
    },
    ocr: {
      currentChar: 'Current Character',
      selectChar: 'Select Character',
      commonChars: 'Common Characters',
      more: 'More',
      char: 'Character',
      position: 'Position',
      selectCharTitle: 'Select Annotation Character',
      inputChar: 'Input Character',
      singleCharRequired: 'Please enter a single character',
      commonCharSets: 'Common Character Sets',
      recentlyUsed: 'Recently Used',
      selectCharFirst: 'Please select a character first'
    },
    preview: {
      toggleAnnotations: 'Toggle Annotations',
      toggleLabels: 'Toggle Labels',
      label: 'Label',
      position: 'Position',
      clickToViewDetails: 'Click to View Details',
      loading: 'Loading...'
    },
    notifications: {
      loadFailed: 'Failed to load annotations',
      saveSuccess: 'Annotations saved successfully',
      saveFailed: 'Failed to save annotations',
      deleteFailed: 'Failed to delete annotation'
    }
  },
  notFound: {
    message: 'Page Not Found',
    backToHome: 'Back to Home'
  },
  generateData: {
    title: 'Generate Data',
    sourceDataset: {
      title: 'Source Dataset',
      name: 'Dataset Name',
      imageCount: '{count} Images',
      annotatedCount: '{count} Annotated'
    },
    targetDataset: {
      title: 'Target Dataset',
      newOption: 'Create New Dataset',
      existingOption: 'Use Existing Dataset',
      sourceOption: 'Use Source Dataset',
      new: {
        name: {
          required: 'Please enter dataset name'
        }
      },
      existing: {
        select: 'Please select target dataset'
      }
    },
    generateOptions: {
      title: 'Generation Options',
      includeAnnotations: 'Include Annotations',
      includeAnnotationsHint: 'If checked, annotations from original images will be copied'
    },
    operations: {
      title: 'Operation Selection',
      available: 'Available Operations',
      selected: 'Selected Operations',
      configure: 'Configure Parameters',
      duplicate: 'Duplicate Operation',
      remove: 'Remove Operation',
      single: 'Single',
      pipeline: 'Pipeline'
    },
    preview: {
      title: 'Preview',
      sourceImage: 'Source Image',
      imageId: 'ID: {id}',
      originalImage: 'Original Image',
      operationResult: {
        single: 'Single',
        pipeline: 'Pipeline'
      }
    },
    actions: {
      preview: 'Generate Preview',
      generate: 'Start Generation'
    },
    progress: {
      title: 'Generation Progress',
      cancel: 'Cancel Generation',
      close: 'Close'
    },
    configuration: {
      title: '{name} Configuration',
      sections: {
        input: 'Input Parameters',
        output: 'Output Parameters'
      },
      params: {
        required: 'Required Parameter',
        optional: 'Optional Parameter',
        defaultValue: 'Default: {value}',
        yes: 'Yes',
        no: 'No'
      },
      imageParam: {
        hint: 'Select image input source',
        useDataset: 'Use Dataset Image',
        upload: 'Upload Custom Image'
      },
      annotationParam: {
        hint: 'Select annotation data source',
        useDataset: 'Use Dataset Annotation',
        custom: 'Custom Annotation Data',
        customHint: 'Please enter valid JSON format annotation data'
      },
      output: {
        hint: 'Select output results to save',
        image: {
          title: 'Image Output',
          noOutput: 'No image output for this operation'
        },
        annotation: {
          title: 'Annotation Output',
          noOutput: 'No annotation output for this operation'
        }
      },
      actions: {
        reset: 'Reset Parameters',
        close: 'Close'
      }
    },
    notifications: {
      loadError: 'Failed to load data',
      previewError: 'Failed to generate preview',
      generateSuccess: 'Data generation completed',
      generateError: 'Failed to generate data',
      cancelConfirm: {
        title: 'Cancel Confirmation',
        message: 'Are you sure you want to cancel the current generation task?',
        canceled: 'Generation task canceled'
      }
    }
  },
  modelTester: {
    selectModel: {
      title: 'Please Select a Model',
      hint: 'Select a trained model from the list to test'
    },
    model: {
      id: 'Model ID'
    },
    params: {
      title: 'Parameter Settings',
      confThreshold: 'Confidence Threshold',
      iouThreshold: 'IOU Threshold'
    },
    image: {
      title: 'Test Image',
      select: 'Select Image',
      test: 'Test Model'
    },
    result: {
      title: 'Test Results',
      noImage: 'Please upload an image to test',
      preview: 'Preview Image',
      detectionResult: 'Detection Result',
      detectedObjects: 'Detected Objects:',
      confidence: 'Confidence',
      noDetection: 'No objects detected'
    },
    notifications: {
      noImageData: 'Failed to get image data',
      noObjectsDetected: 'No objects detected',
      detectionCount: '{count} objects detected',
      testFailed: 'Test failed: {error}',
      testError: 'Test error: {error}'
    }
  },
  alarmPanel: {
    title: {
      info: '',
      warning: '系统警告',
      error: '系统错误',
      critical: '严重故障',
      default: '系统告警'
    },
    actions: {
      acknowledgeAll: '确认所有',
      close: '关闭'
    },
    status: {
      alarmCount: '共 {count} 条告警',
      emergencyStop: '紧急停止'
    },
    notifications: {
      alarmAcknowledged: '告警已确认',
      allAlarmsAcknowledged: '所有告警已确认'
    }
  },
  cameraPreview: {
    loading: '加载摄像头...',
    error: {
      connection: '无法连接到摄像头',
      status: '获取摄像头状态出错:'
    },
    stream: {
      alt: '摄像头画面'
    }
  },
  model: {
    list: {
      title: 'Model List',
      empty: 'No models available',
      create: 'Create Model',
      refresh: 'Refresh List',
      architecture: 'Model Architecture',
      actions: {
        test: 'Test Model',
        delete: 'Delete Model'
      }
    },
    training: {
      title: 'Training Parameters',
      params: {
        architecture: 'Model Architecture',
        epochs: 'Training Epochs',
        batchSize: 'Batch Size',
        imgSize: 'Image Size',
        confThres: 'Confidence Threshold',
        iouThres: 'IOU Threshold'
      },
      start: 'Start Training',
      stop: 'Stop Training',
      modes: {
        config: 'Configure Training',
        test: 'Test Model',
        logs: 'Training Logs',
        files: 'Training Files'
      },
      actions: {
        startTraining: 'Start Training',
        stopTraining: 'Stop Training',
        testModel: 'Test Model',
        viewLogs: 'View Logs',
        viewFiles: 'View Files'
      }
    },
    progress: {
      title: 'Training Progress',
      refresh: 'Refresh Progress',
      epoch: 'Current Epoch',
      loss: 'Loss Value',
      eta: 'Estimated Time Remaining'
    },
    logs: {
      title: 'Training Logs',
      refresh: 'Refresh Logs',
      copy: 'Copy Logs',
      scrollToBottom: 'Scroll to Bottom',
      empty: 'No logs available'
    },
    files: {
      title: 'Model Files',
      refresh: 'Refresh Files',
      root: 'Return to Root',
      download: 'Download File',
      preview: 'Preview File',
      empty: 'No files available',
      actions: {
        root: 'Return to Root',
      }
    },
    dialogs: {
      create: {
        title: 'Create New Model',
        name: 'Model Name',
        nameRequired: 'Please enter a model name',
        dataset: 'Training Dataset',
        datasetRequired: 'Please select a training dataset'
      },
      delete: {
        message: 'Are you sure you want to delete model {name}? This action cannot be undone.'
      }
    },
    notifications: {
      createSuccess: 'Model created successfully',
      createFailed: 'Failed to create model: {error}',
      deleteSuccess: 'Model deleted successfully',
      deleteFailed: 'Failed to delete model: {error}',
      trainStarted: 'Model training started',
      trainFailed: 'Failed to start training: {error}',
      updateParamsFailed: 'Failed to update parameters: {error}',
      loadDatasetsFailed: 'Failed to load datasets',
      copyModelId: 'Model ID copied',
      copyModelIdFailed: 'Failed to copy model ID',
      copyLogs: 'Logs copied',
      copyLogsFailed: 'Failed to copy logs',
      downloadStarted: 'Started downloading {name}'
    },
    status: {
      empty: 'Please select a model',
      emptyHint: 'Select a model from the list on the left, or create a new one',
      notTraining: 'Model is not currently training, no training logs available',
      notCompleted: 'This model has not completed training and cannot be tested',
      selectFeature: 'Please select a feature or operation'
    }
  },
  realtime: {
    title: 'Realtime Monitoring',
    camera: {
      select: 'Select Camera',
      video: 'Camera Video',
      processed: 'Processed Video',
      processing: 'Processing...',
      streamActive: 'Processing Stream Active',
      streamWaiting: 'Waiting for Stream...'
    },
    operation: {
      title: 'Operation Selection',
      select: 'Select Image Processing Operation',
      selectRequired: 'Please select an operation',
      types: {
        single: 'Single',
        pipeline: 'Pipeline'
      },
      apply: 'Apply Operation',
      startStream: 'Start Processing Stream',
      stopStream: 'Stop Processing Stream',
      detection: 'Detection'
    },
    result: {
      title: 'Detection Results',
      waiting: 'Waiting for detection results...',
      status: {
        pass: 'Pass',
        fail: 'Fail'
      },
      details: {
        time: 'Detection Time',
        source: 'Image Source',
        text: 'Recognized Text',
        confidence: 'Confidence',
        error: 'Error Reason',
        filename: 'Filename',
        noText: 'Unable to recognize'
      }
    },
    control: {
      title: 'Camera Control',
      autoDetect: {
        start: 'Start Auto Detection',
        stop: 'Stop Auto Detection'
      },
      capture: 'Single Capture',
      exposure: 'Exposure Time',
      gain: 'Gain'
    },
    notifications: {
      selectCamera: 'Please select a camera first',
      selectOperation: 'Please select an operation first',
      cameraUnavailable: 'Selected camera is currently unavailable',
      startProcessing: 'Starting video processing...',
      invalidOperation: 'Invalid operation information',
      streamStarted: 'Real-time processing started',
      streamStartFailed: 'Failed to start processing stream: {error}',
      stopProcessing: 'Stopping video processing...',
      streamStopped: 'Real-time processing stopped',
      streamError: 'Failed to load processing stream, please check camera and network connection',
      retrying: 'Loading processing stream, retrying...',
      streamConnected: 'Processing stream connected',
      autoDetectStarted: 'Auto detection started',
      autoDetectStopped: 'Auto detection stopped',
      processingComplete: 'Image processing complete',
      processingFailed: 'Failed to process image: {error}',
      uploadImage: 'No active camera stream, please upload an image',
      noCameraControl: 'Camera control not found',
      cameraSelected: 'Selected camera: {name}'
    },
    status: {
      online: 'Online',
      offline: 'Offline',
      error: 'Error',
      unknown: 'Unknown'
    }
  },
  cvOperation: {
    tabs: {
      single: 'Single Operation',
      pipeline: 'Pipeline Operation'
    }
  },
  camera: {
    capture: {
      loading: 'Loading camera...',
      error: 'Failed to load processing stream, please check camera and network connection',
      noCamera: 'No active camera stream, please upload an image',
      uploadedImage: 'Uploaded image, waiting for processing',
      videoStream: 'Video Stream',
      streaming: 'Streaming',
      stopped: 'Stopped',
      useUploadedImage: 'Use uploaded image',
      reupload: 'Reupload',
      capture: 'Capture',
      uploadImage: 'Upload Image',
      stopMonitoring: 'Stop Monitoring',
      startMonitoring: 'Start Monitoring'
    }
  },
  cv: {
    parameter: {
      name: 'Parameter Name',
      nameRequired: 'Please enter parameter name',
      type: 'Parameter Type',
      typeRequired: 'Please select parameter type',
      description: 'Description',
      defaultValue: 'Default Value',
      required: 'Required Parameter'
    },
    operation: {
      new: 'New Operation',
      import: 'Import',
      importTooltip: 'Import operation configuration',
      export: 'Export',
      exportTooltip: 'Export operation configuration',
      delete: 'Delete',
      deleteSelected: 'Delete ({count})',
      deleteTooltip: 'Delete selected operations',
      operationCount: '{count} Operations',
      search: 'Search operation name or description',
      refresh: 'Refresh List',
      columns: {
        name: 'Operation Name',
        description: 'Description',
        createdAt: 'Created At',
        actions: 'Actions'
      },
      actions: {
        edit: 'Edit',
        test: 'Test',
        delete: 'Delete'
      },
      deleteConfirm: {
        title: 'Delete Confirmation',
        singleMessage: 'Are you sure you want to delete operation "{name}"?',
        batchMessage: 'Are you sure you want to delete {count} selected operations?',
        cancel: 'Cancel',
        confirm: 'Delete'
      },
      validation: {
        nameRequired: 'Operation name cannot be empty',
        invalidCode: 'Invalid code format'
      },
      importExport: {
        importErrorDetails: 'Import Error Details',
        exportColumns: {
          name: 'Operation Name',
          description: 'Description',
          code: 'Code',
          inputParams: 'Input Parameters',
          outputParams: 'Output Parameters',
          createdAt: 'Created At',
          updatedAt: 'Updated At'
        },
        exportSheetName: 'Operations',
        exportFileName: 'cv_operations'
      },
      notifications: {
        loadError: 'Failed to load operations',
        saveSuccess: 'Operation saved successfully',
        saveError: 'Failed to save operation',
        deleteSuccess: 'Operation deleted successfully',
        batchDeleteSuccess: 'Operations deleted successfully',
        deleteError: 'Failed to delete operation',
        importFailed: 'Failed to import operation "{name}"',
        importPartialSuccess: 'Import completed: {success} successful, {failed} failed',
        importSuccess: 'Successfully imported {count} operations',
        importError: 'Import failed',
        exportSuccess: 'Successfully exported {count} operations',
        exportError: 'Export failed'
      },
      
    },
    operationEditor: {
      title: {
        edit: 'Edit Operation',
        new: 'New Operation'
      },
      actions: {
        test: 'Run',
        save: 'Save',
        close: 'Close'
      },
      basicInfo: {
        title: 'Basic Information',
        name: 'Operation Name',
        nameRequired: 'Please enter operation name',
        description: 'Description'
      },
      parameters: {
        title: 'Parameter Configuration',
        tabs: {
          input: 'Input Parameters',
          output: 'Output Parameters'
        },
        param: 'Parameter {index}',
        addInput: 'Add Input Parameter',
        addOutput: 'Add Output Parameter'
      },
      codeEditor: {
        title: 'Python Code Editor'
      },
      notifications: {
        initError: 'Failed to initialize editor',
        extractError: 'Failed to extract user code',
        updateError: 'Failed to update code template',
        editorError: 'Failed to get editor content',
        setContentError: 'Failed to set editor content'
      }
    },
    pipeline: {
      new: 'New Pipeline',
      import: 'Import',
      importTooltip: 'Import pipeline configuration',
      export: 'Export',
      exportTooltip: 'Export pipeline configuration',
      delete: 'Delete',
      deleteSelected: 'Delete ({count})',
      deleteTooltip: 'Delete selected pipelines',
      pipelineCount: '{count} Pipelines',
      nodeCount: '{count} Nodes',
      search: 'Search pipeline name or description',
      refresh: 'Refresh List',
      columns: {
        name: 'Pipeline Name',
        description: 'Description',
        nodes: 'Nodes',
        createdAt: 'Created At',
        actions: 'Actions'
      },
      actions: {
        edit: 'Edit',
        test: 'Test',
        delete: 'Delete'
      },
      deleteConfirm: {
        title: 'Delete Confirmation',
        singleMessage: 'Are you sure you want to delete pipeline "{name}"?',
        batchMessage: 'Are you sure you want to delete {count} selected pipelines?',
        cancel: 'Cancel',
        confirm: 'Delete'
      },
      validation: {
        nameRequired: 'Pipeline name cannot be empty',
        metadataRequired: 'Pipeline metadata cannot be empty',
        invalidMetadata: 'Invalid pipeline configuration',
        fileSizeLimit: 'File size cannot exceed 10MB',
        fileTypeError: 'Only .xlsx files are supported',
        missingField: 'Missing required field: {field}'
      },
      importExport: {
        errorDetails: 'Import Error Details',
        columns: {
          name: 'Pipeline Name',
          description: 'Description',
          metadata: 'Metadata',
          inputParams: 'Input Parameters',
          outputParams: 'Output Parameters',
          createdAt: 'Created At',
          updatedAt: 'Updated At'
        },
        sheetName: 'Pipelines',
        fileName: 'pipelines'
      },
      notifications: {
        loadError: 'Failed to load pipelines',
        saveSuccess: 'Pipeline saved successfully',
        saveError: 'Failed to save pipeline',
        deleteSuccess: 'Pipeline deleted successfully',
        batchDeleteSuccess: 'Pipelines deleted successfully',
        deleteError: 'Failed to delete pipeline',
        importFailed: 'Failed to import pipeline "{name}": {error}',
        importPartialSuccess: 'Import completed: {success} successful, {failed} failed',
        importSuccess: 'Successfully imported {count} pipelines',
        importError: 'Import failed',
        exportSuccess: 'Successfully exported {count} pipelines',
        exportError: 'Export failed',
        testPanelError: 'Cannot open test panel: Pipeline does not exist',
        jsonParseError: 'Failed to parse JSON'
      }
    },
    operationTestPanel: {
      title: 'Operation Test',
      actions: {
        run: 'Run',
        close: 'Close'
      },
      input: {
        title: 'Input Parameters',
        jsonFormat: ' (JSON format)'
      },
      output: {
        title: 'Output Results'
      },
      validation: {
        required: 'Required field',
        invalidJson: 'Please enter valid JSON format'
      }
    },
    pipelineEditor: {
      title: {
        new: 'New Pipeline',
        edit: 'Edit Pipeline'
      },
      actions: {
        run: 'Run',
        save: 'Save',
        close: 'Close'
      },
      basicInfo: {
        title: 'Basic Information',
        name: 'Pipeline Name',
        nameRequired: 'Please enter pipeline name',
        description: 'Description'
      },
      nodeToolbox: {
        title: 'Node Toolbox'
      },
      nodeProperties: {
        title: 'Node Properties',
        name: 'Node Name',
        operation: 'Select Operation',
        noOperationFound: 'No matching operation found',
        noDescription: 'No description',
        parameters: {
          title: 'Parameter Configuration',
          valueSource: 'Value Source',
          customValue: 'Custom Value',
          customValueJson: 'Custom Value (JSON Format)'
        }
      },
      flowEditor: {
        title: 'Pipeline Designer',
        undo: 'Undo (Ctrl+Z)',
        redo: 'Redo (Ctrl+Y)',
        delete: 'Delete Selected (Delete)',
        clear: 'Clear Canvas',
        center: 'Center View',
        zoomIn: 'Zoom In',
        zoomOut: 'Zoom Out'
      },
      notifications: {
        cannotDeleteStartEnd: 'Cannot delete start and end nodes',
        initFailed: 'Failed to initialize pipeline designer'
      }
    }
  }
} 
