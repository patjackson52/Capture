package com.capture.app.data

import android.content.Context
import android.net.Uri
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.core.stringSetPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore(name = "capture_prefs")

class PreferencesManager(private val context: Context) {

    companion object {
        private val SAVE_LOCATION_URI = stringPreferencesKey("save_location_uri")
        private val SAVE_LOCATION_DISPLAY = stringPreferencesKey("save_location_display")
        private val TAGS = stringSetPreferencesKey("tags")
    }

    val saveLocationUri: Flow<String?> = context.dataStore.data.map { prefs ->
        prefs[SAVE_LOCATION_URI]
    }

    val saveLocationDisplay: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[SAVE_LOCATION_DISPLAY] ?: "Not set — tap to choose"
    }

    val allTags: Flow<Set<String>> = context.dataStore.data.map { prefs ->
        prefs[TAGS] ?: emptySet()
    }

    suspend fun setSaveLocation(uri: Uri, displayPath: String) {
        context.dataStore.edit { prefs ->
            prefs[SAVE_LOCATION_URI] = uri.toString()
            prefs[SAVE_LOCATION_DISPLAY] = displayPath
        }
    }

    suspend fun addTags(tags: Set<String>) {
        context.dataStore.edit { prefs ->
            val existing = prefs[TAGS] ?: emptySet()
            prefs[TAGS] = existing + tags
        }
    }
}
