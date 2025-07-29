export default {
  common: {
    save: 'حفظ',
    cancel: 'إلغاء',
    delete: 'حذف',
    edit: 'تعديل',
    add: 'إضافة',
    confirm: 'تأكيد',
    minutes: 'دقائق',
    loading: 'جاري التحميل...',
    success: 'نجاح',
    error: 'خطأ',
    warning: 'تحذير',
    info: 'معلومات',
    menu: 'القائمة',
    systemName: 'AI demo HUB'
  },
  settings: {
    system: {
      title: 'إعدادات النظام',
      language: 'لغة النظام',
      autoSaveInterval: 'فاصل الحفظ التلقائي',
      dataRetention: 'احتفاظ البيانات',
      alarmThreshold: 'حد الإنذار'
    },
    mes: {
      title: 'تكامل MES',
      serverUrl: 'عنوان الخادم',
      apiKey: 'مفتاح API',
      testConnection: 'اختبار الاتصال'
    },
    devices: {
      title: 'إدارة الأجهزة',
      all: 'الكل',
      camera: 'كاميرا',
      light: 'إضاءة',
      plc: 'وحدة تحكم',
      disableAutoCheck: 'تعطيل الفحص التلقائي',
      refreshStatus: 'تحديث حالة الجهاز',
      addDevice: 'إضافة جهاز',
      status: {
        online: 'متصل',
        offline: 'غير متصل',
        error: 'خطأ',
        unknown: 'غير معروف'
      },
      preview: {
        setOnline: 'تعيين متصل',
        setOffline: 'تعيين غير متصل',
        edit: 'تعديل الجهاز',
        delete: 'حذف الجهاز',
        title: 'معاينة {name}',
        status: 'حالة الكاميرا',
        streamUrl: 'رابط البث',
        notConfigured: 'غير مهيأ'
      },
      form: {
        title: {
          add: 'إضافة جهاز',
          edit: 'تعديل جهاز'
        },
        name: 'اسم الجهاز',
        type: 'نوع الجهاز',
        model: 'موديل الجهاز',
        config: 'إعدادات الجهاز',
        camera: {
          type: 'نوع الكاميرا',
          types: {
            local: 'كاميرا محلية',
            ip: 'كاميرا IP',
            rtsp: 'بث RTSP',
            http: 'بث HTTP'
          },
          deviceId: 'معرف الجهاز',
          streamUrl: 'رابط الكاميرا'
        },
        light: {
          port: 'منفذ تسلسلي',
          mode: 'وضع التشغيل',
          modes: {
            continuous: 'مستمر',
            flash: 'وميض',
            trigger: 'تشغيل'
          }
        },
        plc: {
          ip: 'عنوان IP',
          rack: 'رقم الرف',
          slot: 'رقم الفتحة'
        }
      },
      noDevices: 'لا توجد أجهزة {type}',
      deleteConfirm: 'هل أنت متأكد من حذف الجهاز "{name}"؟',
      type: {
        camera: 'كاميرا',
        light: 'إضاءة',
        plc: 'وحدة تحكم'
      }
    },
    notifications: {
      savingSettings: 'جاري حفظ إعدادات النظام...',
      settingsSaved: 'تم حفظ إعدادات النظام',
      savingFailed: 'فشل حفظ إعدادات النظام',
      savingMes: 'جاري حفظ إعدادات MES...',
      mesSaved: 'تم حفظ إعدادات MES',
      mesSavingFailed: 'فشل حفظ إعدادات MES',
      loadDevicesFailed: 'فشل تحميل قائمة الأجهزة',
      deviceUpdated: 'تم تحديث الجهاز',
      deviceAdded: 'تمت إضافة الجهاز',
      deviceDeleted: 'تم حذف الجهاز',
      deviceSaveFailed: 'فشل حفظ الجهاز',
      deviceDeleteFailed: 'فشل حذف الجهاز',
      cameraIdError: 'فشل الحصول على معرف الكاميرا، يرجى التحقق من الإعدادات',
      deviceStatusChanged: '{name} {status}',
      deviceStatusUpdateFailed: 'فشل تحديث حالة الجهاز',
      loadSettingsFailed: 'فشل تحميل إعدادات النظام',
      loadMesFailed: 'فشل تحميل إعدادات MES',
      languageChanged: 'تم تغيير اللغة'
    }
  },
  status: {
    cameraList: 'قائمة الكاميرات',
    noCameras: 'لا توجد كاميرات مهيأة',
    camera: 'كاميرا',
    modelList: 'قائمة النماذج',
    noModels: 'لا توجد نماذج محملة',
    model: 'نموذج',
    deviceList: 'قائمة الأجهزة',
    noDevices: 'لا توجد أجهزة تحكم مهيأة',
    device: 'جهاز',
    online: 'متصل',
    offline: 'غير متصل',
    error: 'خطأ',
    connected: 'متصل',
    disconnected: 'غير متصل',
    partiallyConnected: 'متصل جزئياً',
    loaded: 'محمل',
    notLoaded: 'غير محمل'
  },
  emergencyStop: {
    title: 'إيقاف طارئ',
    message: 'تأكيد تنفيذ عملية الإيقاف الطارئ؟ سيؤدي هذا إلى إيقاف جميع عمليات الأجهزة.',
    confirm: 'تأكيد الإيقاف',
    executed: 'تم تنفيذ عملية الإيقاف الطارئ'
  },
  routes: {
    dashboard: 'لوحة التحكم',
    realtime: 'المراقبة المباشرة',
    history: 'السجل',
    annotation: 'تحديد البيانات',
    model: 'تدريب النموذج',
    modelTest: 'اختبار النموذج',
    cvOperations: 'معالجة الصور',
    settings: 'الإعدادات',
    notFound: 'الصفحة غير موجودة'
  },
  dashboard: {
    systemStatus: {
      title: 'حالة النظام',
      uptime: 'وقت التشغيل',
      memory: 'الذاكرة',
      disk: 'القرص',
      systemNormal: 'النظام طبيعي',
      systemLoadHigh: 'حمل النظام مرتفع',
      systemResourceStress: 'ضغط موارد النظام',
      systemStatusError: 'خطأ في حالة النظام',
      days: 'أيام ',
      hours: 'ساعات ',
      minutes: 'دقائق ',
      seconds: 'ثواني ',
      unknown:'مجهول'
    },
    deviceStatus: {
      title: 'حالة الأجهزة',
      onlineRate: 'نسبة الاتصال',
      total: 'الإجمالي',
      online: 'متصل',
      offline: 'غير متصل',
      error: 'خطأ',
      cameras: 'كاميرات'
    },
    detectionStats: {
      title: 'إحصائيات الكشف اليومية',
      comparedToYesterday: 'مقارنة بالأمس ({count}) {change}',
      increase: 'زيادة',
      decrease: 'انخفاض'
    },
    defectStats: {
      title: 'إحصائيات العيوب اليومية',
      comparedToYesterday: 'مقارنة بالأمس ({count}) {change}',
      increase: 'زيادة',
      decrease: 'انخفاض'
    },
    accuracy: {
      title: 'دقة الكشف',
      comparedToYesterday: 'مقارنة بالأمس ({value}%) {change}',
      improve: 'تحسن',
      decrease: 'انخفاض',
      rate: 'الدقة'
    },
    alerts: {
      title: 'التنبيهات الأخيرة',
      new: 'جديد',
      noAlerts: 'لا توجد تنبيهات'
    },
    trend: {
      title: 'اتجاه الكشف (آخر 7 أيام)',
      total: 'الإجمالي',
      pass: 'ناجح',
      fail: 'فاشل'
    }
  },
  history: {
    searchText: 'بحث النص',
    status: {
      title: 'نتيجة الكشف',
      all: 'الكل',
      pass: 'ناجح',
      fail: 'فاشل',
      unknown: 'غير معروف'
    },
    dateRange: 'نطاق التاريخ',
    search: 'بحث',
    export_excel: 'تصدير',
    noData: 'لا توجد سجلات تاريخية',
    detail: {
      title: 'تفاصيل سجل الكشف',
      originalImage: 'الصورة الأصلية',
      processedImage: 'الصورة المعالجة',
      noImage: 'لا توجد صورة',
      timestamp: 'وقت الكشف',
      status: 'نتيجة الكشف',
      text: 'النص المعروف',
      noText: 'غير قادر على التعرف',
      confidence: 'الثقة',
      device: 'الجهاز المستخدم'
    },
    columns: {
      timestamp: 'وقت الكشف',
      text: 'النص المعروف',
      confidence: 'الثقة',
      status: 'نتيجة الكشف',
      device: 'الجهاز المستخدم',
      actions: 'الإجراءات'
    },
    delete: {
      confirm: 'هل أنت متأكد أنك تريد حذف سجل الكشف هذا؟'
    },
    export: {
      loading: 'جاري إعداد تصدير البيانات...',
      noData: 'لا توجد سجلات مطابقة للتصدير',
      success: 'تم تصدير {count} سجلات بنجاح',
      failed: 'فشل التصدير',
      fileName: 'سجل الكشف',
      columns: {
        timestamp: 'وقت الكشف',
        text: 'النص المعروف',
        confidence: 'الثقة',
        status: 'نتيجة الكشف',
        device: 'الجهاز المستخدم',
        imageUrl: 'رابط الصورة',
        processedImageUrl: 'رابط الصورة المعالجة'
      }
    }
  },
  annotation: {
    datasets: {
      title: 'مجموعات البيانات',
      create: 'مجموعة بيانات جديدة',
      count: '{count} مجموعات بيانات',
      imageCount: '{count} صور'
    },
    selectDataset: 'الرجاء اختيار مجموعة بيانات',
    selectImage: 'الرجاء اختيار صورة',
    selectImageHint: 'اختر صورة من القائمة على اليسار للتعليق عليها',
    actions: {
      deleteSelected: 'حذف المحدد',
      upload: 'رفع الصور',
      rename: 'إعادة تسمية',
      gridView: 'عرض الشبكة',
      annotationView: 'عرض التعليقات',
      export: 'تصدير مجموعة البيانات',
      import: 'استيراد مجموعة البيانات',
      generate: 'إنشاء بيانات',
      more: 'المزيد',
      deleteDataset: 'حذف مجموعة البيانات'
    },
    dialogs: {
      upload: {
        title: 'رفع الصور',
        selectFiles: 'اختر الصور',
        upload: 'رفع'
      },
      create: {
        title: 'مجموعة بيانات جديدة',
        name: 'اسم مجموعة البيانات',
        nameRequired: 'الرجاء إدخال اسم مجموعة البيانات',
        type: 'نوع مجموعة البيانات',
        create: 'إنشاء'
      },
      rename: {
        title: 'إعادة تسمية مجموعة البيانات',
        name: 'اسم مجموعة البيانات',
        nameRequired: 'الرجاء إدخال اسم مجموعة البيانات'
      },
      delete: {
        title: 'تأكيد الحذف',
        confirmImages: 'هل أنت متأكد أنك تريد حذف {count} من الصور المحددة؟ لا يمكن التراجع عن هذا الإجراء.',
        confirmDataset: 'هل أنت متأكد أنك تريد حذف مجموعة البيانات "{name}"؟ لا يمكن التراجع عن هذا الإجراء.'
      }
    },
    datasetTypes: {
      textRegion: 'مجموعة بيانات منطقة النص',
      ocr: 'مجموعة بيانات التعرف على النصوص'
    },
    notifications: {
      loadDatasetsFailed: 'فشل تحميل مجموعات البيانات، يرجى المحاولة مرة أخرى',
      createDatasetSuccess: 'تم إنشاء مجموعة البيانات بنجاح',
      createDatasetFailed: 'فشل إنشاء مجموعة البيانات، يرجى المحاولة مرة أخرى',
      renameSuccess: 'تم إعادة التسمية بنجاح',
      renameFailed: 'فشل إعادة التسمية، يرجى المحاولة مرة أخرى',
      deleteDatasetSuccess: 'تم حذف مجموعة البيانات بنجاح',
      deleteDatasetFailed: 'فشل حذف مجموعة البيانات، يرجى المحاولة مرة أخرى',
      deleteImageSuccess: 'تم حذف الصورة بنجاح',
      deleteImageFailed: 'فشل حذف الصورة، يرجى المحاولة مرة أخرى'
    }
  },
  annotator: {
    controls: {
      zoomIn: 'تكبير',
      zoomOut: 'تصغير',
      save: 'حفظ التعليقات',
      reload: 'إعادة تحميل',
      deleteSelectedChar: 'حذف المحدد ({char})',
      cancelDrawing: 'إلغاء الرسم',
      closeDetails: 'إغلاق التفاصيل',
      enterFullscreen: 'الدخول إلى وضع ملء الشاشة',
      exitFullscreen: 'الخروج من وضع ملء الشاشة',
      deleteSelected: 'حذف المحدد'
    },
    tools: {
      textRegion: 'منطقة النص (مضلع)',
      character: 'الحرف (مستطيل)',
      wheelText: 'نص العجلة (مستطيل)'
    },
    ocr: {
      currentChar: 'الحرف الحالي',
      selectChar: 'اختر الحرف',
      commonChars: 'الحروف الشائعة',
      more: 'المزيد',
      char: 'الحرف',
      position: 'الموضع',
      selectCharTitle: 'اختر حرف التعليق',
      inputChar: 'أدخل الحرف',
      singleCharRequired: 'الرجاء إدخال حرف واحد',
      commonCharSets: 'مجموعات الحروف الشائعة',
      recentlyUsed: 'المستخدمة مؤخراً',
      selectCharFirst: 'الرجاء اختيار حرف أولاً'
    },
    preview: {
      toggleAnnotations: 'تبديل التعليقات',
      toggleLabels: 'تبديل التسميات',
      label: 'التسمية',
      position: 'الموضع',
      clickToViewDetails: 'انقر لعرض التفاصيل',
      loading: 'جاري التحميل...'
    },
    notifications: {
      loadFailed: 'فشل تحميل التعليقات',
      saveSuccess: 'تم حفظ التعليقات بنجاح',
      saveFailed: 'فشل حفظ التعليقات',
      deleteFailed: 'فشل حذف التعليق'
    }
  },
  notFound: {
    message: 'الصفحة غير موجودة',
    backToHome: 'العودة إلى الصفحة الرئيسية'
  },
  generateData: {
    title: 'إنشاء بيانات',
    sourceDataset: {
      title: 'مجموعة البيانات المصدر',
      name: 'اسم مجموعة البيانات',
      imageCount: '{count} صور',
      annotatedCount: '{count} معلق عليها'
    },
    targetDataset: {
      title: 'مجموعة البيانات الهدف',
      newOption: 'إنشاء مجموعة بيانات جديدة',
      existingOption: 'استخدام مجموعة بيانات موجودة',
      sourceOption: 'استخدام مجموعة البيانات المصدر',
      new: {
        name: {
          required: 'الرجاء إدخال اسم مجموعة البيانات'
        }
      },
      existing: {
        select: 'الرجاء اختيار مجموعة البيانات الهدف'
      }
    },
    generateOptions: {
      title: 'خيارات الإنشاء',
      includeAnnotations: 'تضمين التعليقات',
      includeAnnotationsHint: 'إذا تم تحديده، سيتم نسخ التعليقات من الصور الأصلية'
    },
    operations: {
      title: 'اختيار العمليات',
      available: 'العمليات المتاحة',
      selected: 'العمليات المحددة',
      configure: 'تكوين المعلمات',
      duplicate: 'تكرار العملية',
      remove: 'إزالة العملية',
      single: 'مفرد',
      pipeline: 'خط أنابيب'
    },
    preview: {
      title: 'معاينة',
      sourceImage: 'الصورة المصدر',
      imageId: 'المعرف: {id}',
      originalImage: 'الصورة الأصلية',
      operationResult: {
        single: 'مفرد',
        pipeline: 'خط أنابيب'
      }
    },
    actions: {
      preview: 'إنشاء معاينة',
      generate: 'بدء الإنشاء'
    },
    progress: {
      title: 'تقدم الإنشاء',
      cancel: 'إلغاء الإنشاء',
      close: 'إغلاق'
    },
    configuration: {
      title: 'تكوين {name}',
      sections: {
        input: 'معلمات الإدخال',
        output: 'معلمات الإخراج'
      },
      params: {
        required: 'معلمة مطلوبة',
        optional: 'معلمة اختيارية',
        defaultValue: 'القيمة الافتراضية: {value}',
        yes: 'نعم',
        no: 'لا'
      },
      imageParam: {
        hint: 'اختر مصدر إدخال الصورة',
        useDataset: 'استخدام صورة مجموعة البيانات',
        upload: 'رفع صورة مخصصة'
      },
      annotationParam: {
        hint: 'اختر مصدر بيانات التعليق',
        useDataset: 'استخدام تعليق مجموعة البيانات',
        custom: 'بيانات تعليق مخصصة',
        customHint: 'الرجاء إدخال بيانات تعليق بتنسيق JSON صالح'
      },
      output: {
        hint: 'اختر نتائج الإخراج للحفظ',
        image: {
          title: 'مخرجات الصورة',
          noOutput: 'لا توجد مخرجات صورة لهذه العملية'
        },
        annotation: {
          title: 'مخرجات التعليق التوضيحي',
          noOutput: 'لا توجد مخرجات تعليق توضيحي لهذه العملية'
        }
      },
      actions: {
        reset: 'إعادة تعيين المعلمات',
        close: 'إغلاق'
      }
    },
    notifications: {
      loadError: 'فشل في تحميل البيانات',
      previewError: 'فشل في إنشاء المعاينة',
      generateSuccess: 'اكتمل إنشاء البيانات',
      generateError: 'فشل في إنشاء البيانات',
      cancelConfirm: {
        title: 'تأكيد الإلغاء',
        message: 'هل أنت متأكد أنك تريد إلغاء مهمة الإنشاء الحالية؟',
        canceled: 'تم إلغاء مهمة الإنشاء'
      }
    }
  },
  modelTester: {
    selectModel: {
      title: 'الرجاء اختيار نموذج',
      hint: 'اختر نموذجاً مدرباً من القائمة للاختبار'
    },
    model: {
      id: 'معرف النموذج'
    },
    params: {
      title: 'إعدادات المعلمات',
      confThreshold: 'عتبة الثقة',
      iouThreshold: 'عتبة التداخل'
    },
    image: {
      title: 'صورة الاختبار',
      select: 'اختر صورة',
      test: 'اختبار النموذج'
    },
    result: {
      title: 'نتائج الاختبار',
      noImage: 'الرجاء رفع صورة للاختبار',
      preview: 'معاينة الصورة',
      detectionResult: 'نتيجة الكشف',
      detectedObjects: 'الكائنات المكتشفة:',
      confidence: 'مستوى الثقة',
      noDetection: 'لم يتم اكتشاف أي كائنات'
    },
    notifications: {
      noImageData: 'فشل في الحصول على بيانات الصورة',
      noObjectsDetected: 'لم يتم اكتشاف أي كائنات',
      detectionCount: 'تم اكتشاف {count} كائنات',
      testFailed: 'فشل الاختبار: {error}',
      testError: 'خطأ في الاختبار: {error}'
    }
  },
  alarmPanel: {
    title: {
      info: '',
      warning: 'تحذير النظام',
      error: 'خطأ في النظام',
      critical: 'عطل خطير',
      default: 'تنبيه النظام'
    },
    actions: {
      acknowledgeAll: 'تأكيد الكل',
      close: 'إغلاق'
    },
    status: {
      alarmCount: 'إجمالي {count} تنبيهاً',
      emergencyStop: 'إيقاف طارئ'
    },
    notifications: {
      alarmAcknowledged: 'تم تأكيد التنبيه',
      allAlarmsAcknowledged: 'تم تأكيد جميع التنبيهات'
    }
  },
  cameraPreview: {
    loading: 'جاري تحميل الكاميرا...',
    error: {
      connection: 'تعذر الاتصال بالكاميرا',
      status: 'خطأ في الحصول على حالة الكاميرا:'
    },
    stream: {
      alt: 'مشهد الكاميرا'
    }
  },
  model: {
    list: {
      title: 'قائمة النماذج',
      empty: 'لا توجد نماذج متاحة',
      create: 'إنشاء نموذج',
      refresh: 'تحديث القائمة',
      architecture: 'هندسة النموذج',
      actions: {
        test: 'نموذج الاختبار',
        delete: 'حذف النموذج'
      }
    },
    training: {
      title: 'معلمات التدريب',
      params: {
        architecture: 'هندسة النموذج',
        epochs: 'دورات التدريب',
        batchSize: 'حجم الدفعة',
        imgSize: 'حجم الصورة',
        confThres: 'عتبة الثقة',
        iouThres: 'عتبة التداخل'
      },
      start: 'بدء التدريب',
      stop: 'إيقاف التدريب',
      modes: {
        config: 'تكوين التدريب',
        test: 'اختبار النموذج',
        logs: 'سجلات التدريب',
        files: 'ملفات التدريب'
      },
      actions: {
        startTraining: 'ابدأ التدريب',
        stopTraining: 'توقف عن التدريب',
        testModel: 'Test Model',
        viewLogs: 'View Logs',
        viewFiles: 'View Files'
      }
    },
    progress: {
      title: 'تقدم التدريب',
      refresh: 'تحديث التقدم',
      epoch: 'الدورة الحالية',
      loss: 'قيمة الخسارة',
      eta: 'الوقت المتبقي المقدر'
    },
    logs: {
      title: 'سجلات التدريب',
      refresh: 'تحديث السجلات',
      copy: 'نسخ السجلات',
      scrollToBottom: 'التمرير إلى الأسفل',
      empty: 'لا توجد سجلات متاحة'
    },
    files: {
      title: 'ملفات النموذج',
      refresh: 'تحديث الملفات',
      root: 'العودة إلى الجذر',
      download: 'تحميل الملف',
      preview: 'معاينة الملف',
      empty: 'لا توجد ملفات متاحة',
      actions: {
        root: 'العودة إلى الجذر',
      }
    },
    dialogs: {
      create: {
        title: 'إنشاء نموذج جديد',
        name: 'اسم النموذج',
        nameRequired: 'الرجاء إدخال اسم النموذج',
        dataset: 'مجموعة بيانات التدريب',
        datasetRequired: 'الرجاء اختيار مجموعة بيانات التدريب'
      },
      delete: {
        message: 'هل أنت متأكد أنك تريد حذف النموذج {name}؟ لا يمكن التراجع عن هذا الإجراء.'
      }
    },
    notifications: {
      createSuccess: 'تم إنشاء النموذج بنجاح',
      createFailed: 'فشل في إنشاء النموذج: {error}',
      deleteSuccess: 'تم حذف النموذج بنجاح',
      deleteFailed: 'فشل في حذف النموذج: {error}',
      trainStarted: 'بدأ تدريب النموذج',
      trainFailed: 'فشل في بدء التدريب: {error}',
      updateParamsFailed: 'فشل في تحديث المعلمات: {error}',
      loadDatasetsFailed: 'فشل في تحميل مجموعات البيانات',
      copyModelId: 'تم نسخ معرف النموذج',
      copyModelIdFailed: 'فشل في نسخ معرف النموذج',
      copyLogs: 'تم نسخ السجلات',
      copyLogsFailed: 'فشل في نسخ السجلات',
      downloadStarted: 'بدأ تحميل {name}'
    },
    status: {
      empty: 'الرجاء اختيار نموذج',
      emptyHint: 'اختر نموذجاً من القائمة على اليسار، أو أنشئ نموذجاً جديداً',
      notTraining: 'النموذج لا يتم تدريبه حالياً، لا توجد سجلات تدريب متاحة',
      notCompleted: 'لم يكتمل تدريب هذا النموذج ولا يمكن اختباره',
      selectFeature: 'الرجاء اختيار ميزة أو عملية'
    }
  },
  realtime: {
    title: 'المراقبة في الوقت الفعلي',
    camera: {
      select: 'اختر الكاميرا',
      video: 'فيديو الكاميرا',
      processed: 'الفيديو المعالج',
      processing: 'جاري المعالجة...',
      streamActive: 'تيار المعالجة نشط',
      streamWaiting: 'في انتظار التيار...'
    },
    operation: {
      title: 'اختيار العملية',
      select: 'اختر عملية معالجة الصور',
      selectRequired: 'الرجاء اختيار عملية',
      types: {
        single: 'مفرد',
        pipeline: 'خط أنابيب'
      },
      apply: 'تطبيق العملية',
      startStream: 'بدء تيار المعالجة',
      stopStream: 'إيقاف تيار المعالجة',
      detection: 'الكشف'
    },
    result: {
      title: 'نتائج الكشف',
      waiting: 'في انتظار نتائج الكشف...',
      status: {
        pass: 'ناجح',
        fail: 'فشل'
      },
      details: {
        time: 'وقت الكشف',
        source: 'مصدر الصورة',
        text: 'النص المعترف به',
        confidence: 'مستوى الثقة',
        error: 'سبب الخطأ',
        filename: 'اسم الملف',
        noText: 'تعذر التعرف'
      }
    },
    control: {
      title: 'تحكم الكاميرا',
      autoDetect: {
        start: 'بدء الكشف التلقائي',
        stop: 'إيقاف الكشف التلقائي'
      },
      capture: 'التقاط واحد',
      exposure: 'وقت التعريض',
      gain: 'التكبير'
    },
    notifications: {
      selectCamera: 'الرجاء اختيار كاميرا أولاً',
      selectOperation: 'الرجاء اختيار عملية أولاً',
      cameraUnavailable: 'الكاميرا المحددة غير متوفرة حالياً',
      startProcessing: 'جاري بدء معالجة الفيديو...',
      invalidOperation: 'معلومات العملية غير صالحة',
      streamStarted: 'تم بدء المعالجة في الوقت الفعلي',
      streamStartFailed: 'فشل بدء تيار المعالجة: {error}',
      stopProcessing: 'جاري إيقاف معالجة الفيديو...',
      streamStopped: 'تم إيقاف المعالجة في الوقت الفعلي',
      streamError: 'فشل تحميل تيار المعالجة، يرجى التحقق من الكاميرا واتصال الشبكة',
      retrying: 'جاري تحميل تيار المعالجة، إعادة المحاولة...',
      streamConnected: 'تم الاتصال بتيار المعالجة',
      autoDetectStarted: 'تم بدء الكشف التلقائي',
      autoDetectStopped: 'تم إيقاف الكشف التلقائي',
      processingComplete: 'اكتملت معالجة الصورة',
      processingFailed: 'فشل معالجة الصورة: {error}',
      uploadImage: 'لا يوجد تيار كاميرا نشط، يرجى رفع صورة',
      noCameraControl: 'لم يتم العثور على تحكم الكاميرا',
      cameraSelected: 'الكاميرا المحددة: {name}'
    },
    status: {
      online: 'متصل',
      offline: 'غير متصل',
      error: 'خطأ',
      unknown: 'غير معروف'
    }
  },
  cvOperation: {
    tabs: {
      single: 'عملية مفردة',
      pipeline: 'عملية خط أنابيب'
    }
  },
  camera: {
    capture: {
      loading: 'جاري تحميل الكاميرا...',
      error: 'فشل تحميل تيار المعالجة، يرجى التحقق من الكاميرا واتصال الشبكة',
      noCamera: 'لا يوجد تيار كاميرا نشط، يرجى رفع صورة',
      uploadedImage: 'تم رفع الصورة، في انتظار المعالجة',
      videoStream: 'تيار الفيديو',
      streaming: 'جاري البث',
      stopped: 'متوقف',
      useUploadedImage: 'استخدام الصورة المرفوعة',
      reupload: 'إعادة الرفع',
      capture: 'التقاط',
      uploadImage: 'رفع صورة',
      stopMonitoring: 'إيقاف المراقبة',
      startMonitoring: 'بدء المراقبة'
    }
  },
  cv: {
    parameter: {
      name: 'اسم المعامل',
      nameRequired: 'الرجاء إدخال اسم المعامل',
      type: 'نوع المعامل',
      typeRequired: 'الرجاء اختيار نوع المعامل',
      description: 'الوصف',
      defaultValue: 'القيمة الافتراضية',
      required: 'معامل مطلوب'
    },
    operation: {
      new: 'عملية جديدة',
      import: 'استيراد',
      importTooltip: 'استيراد تكوين العملية',
      export: 'تصدير',
      exportTooltip: 'تصدير تكوين العملية',
      delete: 'حذف',
      deleteSelected: 'حذف ({count})',
      deleteTooltip: 'حذف العمليات المحددة',
      operationCount: '{count} عمليات',
      search: 'البحث عن اسم العملية أو الوصف',
      refresh: 'تحديث القائمة',
      columns: {
        name: 'اسم العملية',
        description: 'الوصف',
        createdAt: 'تاريخ الإنشاء',
        actions: 'الإجراءات'
      },
      actions: {
        edit: 'تعديل',
        test: 'اختبار',
        delete: 'حذف'
      },
      deleteConfirm: {
        title: 'تأكيد الحذف',
        singleMessage: 'هل أنت متأكد من حذف العملية "{name}"؟',
        batchMessage: 'هل أنت متأكد من حذف {count} من العمليات المحددة؟',
        cancel: 'إلغاء',
        confirm: 'حذف'
      },
      validation: {
        nameRequired: 'اسم العملية لا يمكن أن يكون فارغاً',
        invalidCode: 'تنسيق الكود غير صالح'
      },
      importExport: {
        importErrorDetails: 'تفاصيل خطأ الاستيراد',
        exportColumns: {
          name: 'اسم العملية',
          description: 'الوصف',
          code: 'الكود',
          inputParams: 'معاملات الإدخال',
          outputParams: 'معاملات الإخراج',
          createdAt: 'تاريخ الإنشاء',
          updatedAt: 'تاريخ التحديث'
        },
        exportSheetName: 'العمليات',
        exportFileName: 'cv_operations'
      },
      notifications: {
        loadError: 'فشل تحميل العمليات',
        saveSuccess: 'تم حفظ العملية بنجاح',
        saveError: 'فشل حفظ العملية',
        deleteSuccess: 'تم حذف العملية بنجاح',
        batchDeleteSuccess: 'تم حذف العمليات بنجاح',
        deleteError: 'فشل حذف العملية',
        importFailed: 'فشل استيراد العملية "{name}"',
        importPartialSuccess: 'اكتمل الاستيراد: {success} نجاح، {failed} فشل',
        importSuccess: 'تم استيراد {count} عمليات بنجاح',
        importError: 'فشل الاستيراد',
        exportSuccess: 'تم تصدير {count} عمليات بنجاح',
        exportError: 'فشل التصدير'
      }
    },
    operationEditor: {
      title: {
        edit: 'تعديل العملية',
        new: 'عملية جديدة'
      },
      actions: {
        test: 'تشغيل',
        save: 'حفظ',
        close: 'إغلاق'
      },
      basicInfo: {
        title: 'المعلومات الأساسية',
        name: 'اسم العملية',
        nameRequired: 'الرجاء إدخال اسم العملية',
        description: 'الوصف'
      },
      parameters: {
        title: 'تكوين المعاملات',
        tabs: {
          input: 'معاملات الإدخال',
          output: 'معاملات الإخراج'
        },
        param: 'المعامل {index}',
        addInput: 'إضافة معامل إدخال',
        addOutput: 'إضافة معامل إخراج'
      },
      codeEditor: {
        title: 'محرر كود Python'
      },
      notifications: {
        initError: 'فشل تهيئة المحرر',
        extractError: 'فشل استخراج كود المستخدم',
        updateError: 'فشل تحديث قالب الكود',
        editorError: 'فشل الحصول على محتوى المحرر',
        setContentError: 'فشل تعيين محتوى المحرر'
      }
    },
    pipeline: {
      new: 'خط أنابيب جديد',
      import: 'استيراد',
      importTooltip: 'استيراد تكوين خط الأنابيب',
      export: 'تصدير',
      exportTooltip: 'تصدير تكوين خط الأنابيب',
      delete: 'حذف',
      deleteSelected: 'حذف ({count})',
      deleteTooltip: 'حذف خطوط الأنابيب المحددة',
      pipelineCount: '{count} خطوط أنابيب',
      nodeCount: '{count} عقد',
      search: 'البحث عن اسم خط الأنابيب أو الوصف',
      refresh: 'تحديث القائمة',
      columns: {
        name: 'اسم خط الأنابيب',
        description: 'الوصف',
        nodes: 'العقد',
        createdAt: 'تاريخ الإنشاء',
        actions: 'الإجراءات'
      },
      actions: {
        edit: 'تعديل',
        test: 'اختبار',
        delete: 'حذف'
      },
      deleteConfirm: {
        title: 'تأكيد الحذف',
        singleMessage: 'هل أنت متأكد من حذف خط الأنابيب "{name}"؟',
        batchMessage: 'هل أنت متأكد من حذف {count} من خطوط الأنابيب المحددة؟',
        cancel: 'إلغاء',
        confirm: 'حذف'
      },
      validation: {
        nameRequired: 'اسم خط الأنابيب لا يمكن أن يكون فارغاً',
        metadataRequired: 'بيانات خط الأنابيب لا يمكن أن تكون فارغة',
        invalidMetadata: 'تكوين خط الأنابيب غير صالح',
        fileSizeLimit: 'لا يمكن أن يتجاوز حجم الملف 10 ميجابايت',
        fileTypeError: 'يتم دعم ملفات .xlsx فقط',
        missingField: 'حقل مطلوب مفقود: {field}'
      },
      importExport: {
        errorDetails: 'تفاصيل خطأ الاستيراد',
        columns: {
          name: 'اسم خط الأنابيب',
          description: 'الوصف',
          metadata: 'البيانات الوصفية',
          inputParams: 'معاملات الإدخال',
          outputParams: 'معاملات الإخراج',
          createdAt: 'تاريخ الإنشاء',
          updatedAt: 'تاريخ التحديث'
        },
        sheetName: 'خطوط الأنابيب',
        fileName: 'خطوط_الأنابيب'
      },
      notifications: {
        loadError: 'فشل تحميل خطوط الأنابيب',
        saveSuccess: 'تم حفظ خط الأنابيب بنجاح',
        saveError: 'فشل حفظ خط الأنابيب',
        deleteSuccess: 'تم حذف خط الأنابيب بنجاح',
        batchDeleteSuccess: 'تم حذف خطوط الأنابيب بنجاح',
        deleteError: 'فشل حذف خط الأنابيب',
        importFailed: 'فشل استيراد خط الأنابيب "{name}": {error}',
        importPartialSuccess: 'اكتمل الاستيراد: {success} ناجح، {failed} فاشل',
        importSuccess: 'تم استيراد {count} من خطوط الأنابيب بنجاح',
        importError: 'فشل الاستيراد',
        exportSuccess: 'تم تصدير {count} من خطوط الأنابيب بنجاح',
        exportError: 'فشل التصدير',
        testPanelError: 'لا يمكن فتح لوحة الاختبار: خط الأنابيب غير موجود',
        jsonParseError: 'فشل تحليل JSON'
      }
    },
    operationTestPanel: {
      title: 'اختبار العملية',
      actions: {
        run: 'تشغيل',
        close: 'إغلاق'
      },
      input: {
        title: 'معاملات الإدخال',
        jsonFormat: ' (تنسيق JSON)'
      },
      output: {
        title: 'نتائج الإخراج'
      },
      validation: {
        required: 'حقل مطلوب',
        invalidJson: 'الرجاء إدخال تنسيق JSON صالح'
      }
    },
    pipelineEditor: {
      title: {
        new: 'خط أنابيب جديد',
        edit: 'تعديل خط الأنابيب'
      },
      actions: {
        run: 'تشغيل',
        save: 'حفظ',
        close: 'إغلاق'
      },
      basicInfo: {
        title: 'المعلومات الأساسية',
        name: 'اسم خط الأنابيب',
        nameRequired: 'الرجاء إدخال اسم خط الأنابيب',
        description: 'الوصف'
      },
      nodeToolbox: {
        title: 'صندوق أدوات العقد'
      },
      nodeProperties: {
        title: 'خصائص العقدة',
        name: 'اسم العقدة',
        operation: 'اختر العملية',
        noOperationFound: 'لم يتم العثور على عملية مطابقة',
        noDescription: 'لا يوجد وصف',
        parameters: {
          title: 'تكوين المعاملات',
          valueSource: 'مصدر القيمة',
          customValue: 'قيمة مخصصة',
          customValueJson: 'قيمة مخصصة (تنسيق JSON)'
        }
      },
      flowEditor: {
        title: 'مصمم خط الأنابيب',
        undo: 'تراجع (Ctrl+Z)',
        redo: 'إعادة (Ctrl+Y)',
        delete: 'حذف المحدد (Delete)',
        clear: 'مسح اللوحة',
        center: 'توسيط العرض',
        zoomIn: 'تكبير',
        zoomOut: 'تصغير'
      },
      notifications: {
        cannotDeleteStartEnd: 'لا يمكن حذف عقد البداية والنهاية',
        initFailed: 'فشل تهيئة مصمم خط الأنابيب'
      }
    }
  }
}