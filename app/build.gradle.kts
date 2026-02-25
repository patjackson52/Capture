plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.compose.compiler)
}

android {
    namespace = "com.capture.app"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.capture.app"
        minSdk = 26
        targetSdk = 35
        versionCode = 2
        versionName = "0.1.0-alpha.1"
    }

    val ciStoreFile = providers.gradleProperty("ANDROID_SIGNING_STORE_FILE").orNull
    val ciStorePassword = providers.gradleProperty("ANDROID_SIGNING_STORE_PASSWORD").orNull
    val ciKeyAlias = providers.gradleProperty("ANDROID_SIGNING_KEY_ALIAS").orNull
    val ciKeyPassword = providers.gradleProperty("ANDROID_SIGNING_KEY_PASSWORD").orNull
    val ciSigningReady = listOf(ciStoreFile, ciStorePassword, ciKeyAlias, ciKeyPassword).all { !it.isNullOrBlank() }

    signingConfigs {
        if (ciSigningReady) {
            create("ciRelease") {
                storeFile = file(ciStoreFile!!)
                storePassword = ciStorePassword
                keyAlias = ciKeyAlias
                keyPassword = ciKeyPassword
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            if (ciSigningReady) {
                signingConfig = signingConfigs.getByName("ciRelease")
            }
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation(libs.androidx.material.icons.extended)
    implementation(libs.androidx.datastore.preferences)
    implementation(libs.androidx.documentfile)
    debugImplementation(libs.androidx.ui.tooling)
}
