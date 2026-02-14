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

class MainActivity : ComponentActivity() {

    private val prefs by lazy { PreferencesManager(this) }

    private val folderPickerLauncher = registerForActivityResult(
        ActivityResultContracts.OpenDocumentTree()
    ) { uri: Uri? ->
        uri?.let { treeUri ->
            // Take persistable permission so we can write here across reboots
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
        setContent {
            CaptureTheme {
                CaptureScreen(
                    source = CaptureSource.Direct,
                    onSaved = {
                        Toast.makeText(this, "Captured!", Toast.LENGTH_SHORT).show()
                        // Reset for next capture — just recreate
                        recreate()
                    },
                    onFolderPick = { folderPickerLauncher.launch(null) }
                )
            }
        }
    }

    private fun extractDisplayPath(uri: Uri): String {
        // DocumentTree URIs look like: content://com.android.externalstorage.documents/tree/primary:Documents/Capture
        // Extract the human-readable part after "tree/"
        val path = uri.lastPathSegment ?: uri.toString()
        return path.replace("primary:", "Internal/").replace(":", "/")
    }
}
