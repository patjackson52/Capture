package com.capture.app

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.lifecycle.lifecycleScope
import com.capture.app.data.PreferencesManager
import com.capture.app.model.CaptureSource
import com.capture.app.ui.CaptureScreen
import com.capture.app.ui.theme.CaptureTheme
import kotlinx.coroutines.launch

/**
 * Handles ACTION_PROCESS_TEXT — appears in the text selection menu
 * next to Copy/Paste in any app (API 23+).
 */
class ProcessTextActivity : ComponentActivity() {

    private val prefs by lazy { PreferencesManager(this) }

    private val folderPickerLauncher = registerForActivityResult(
        ActivityResultContracts.OpenDocumentTree()
    ) { uri: Uri? ->
        uri?.let { treeUri ->
            val flags = Intent.FLAG_GRANT_READ_URI_PERMISSION or
                    Intent.FLAG_GRANT_WRITE_URI_PERMISSION
            contentResolver.takePersistableUriPermission(treeUri, flags)
            val displayPath = extractDisplayPath(treeUri)
            lifecycleScope.launch {
                prefs.setSaveLocation(treeUri, displayPath)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val selectedText = intent.getCharSequenceExtra(Intent.EXTRA_PROCESS_TEXT)?.toString() ?: ""

        setContent {
            CaptureTheme {
                CaptureScreen(
                    initialText = selectedText,
                    source = CaptureSource.ProcessText,
                    onSaved = {
                        Toast.makeText(this, "Captured!", Toast.LENGTH_SHORT).show()
                        finish()
                    },
                    onFolderPick = { folderPickerLauncher.launch(null) }
                )
            }
        }
    }

    private fun extractDisplayPath(uri: Uri): String {
        val path = uri.lastPathSegment ?: uri.toString()
        return path.replace("primary:", "Internal/").replace(":", "/")
    }
}
