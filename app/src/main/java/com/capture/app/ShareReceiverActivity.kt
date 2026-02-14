package com.capture.app

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Parcelable
import android.provider.OpenableColumns
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.lifecycleScope
import com.capture.app.data.PreferencesManager
import com.capture.app.model.Attachment
import com.capture.app.model.CaptureSource
import com.capture.app.ui.CaptureScreen
import com.capture.app.ui.LogViewerScreen
import com.capture.app.ui.theme.CaptureTheme
import kotlinx.coroutines.launch

class ShareReceiverActivity : ComponentActivity() {

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

    private var showLogs by mutableStateOf(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val (text, attachments) = extractSharedContent(intent)

        setContent {
            CaptureTheme {
                if (showLogs) {
                    LogViewerScreen(onBack = { showLogs = false })
                } else {
                    CaptureScreen(
                        initialText = text,
                        initialAttachments = attachments,
                        source = CaptureSource.Share,
                        onSaved = {
                            Toast.makeText(this, "Captured!", Toast.LENGTH_SHORT).show()
                            finish()
                        },
                        onFolderPick = { folderPickerLauncher.launch(null) },
                        onViewLogs = { showLogs = true }
                    )
                }
            }
        }
    }

    private fun extractSharedContent(intent: Intent): Pair<String, List<Attachment>> {
        val text = buildString {
            intent.getStringExtra(Intent.EXTRA_SUBJECT)?.let {
                appendLine(it)
                appendLine()
            }
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let {
                append(it)
            }
        }.trim()

        val attachments = mutableListOf<Attachment>()

        when (intent.action) {
            Intent.ACTION_SEND -> {
                getParcelableExtraCompat<Uri>(intent, Intent.EXTRA_STREAM)?.let { uri ->
                    attachments.add(uriToAttachment(uri))
                }
            }
            Intent.ACTION_SEND_MULTIPLE -> {
                getParcelableArrayListExtraCompat<Uri>(intent, Intent.EXTRA_STREAM)?.forEach { uri ->
                    attachments.add(uriToAttachment(uri))
                }
            }
        }

        return Pair(text, attachments)
    }

    private fun uriToAttachment(uri: Uri): Attachment {
        val mimeType = contentResolver.getType(uri)
        val displayName = queryDisplayName(uri)
        return Attachment(uri = uri, mimeType = mimeType, displayName = displayName)
    }

    private fun queryDisplayName(uri: Uri): String? {
        return try {
            contentResolver.query(uri, null, null, null, null)?.use { cursor ->
                if (cursor.moveToFirst()) {
                    val idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                    if (idx >= 0) cursor.getString(idx) else null
                } else null
            }
        } catch (_: Exception) {
            null
        }
    }

    @Suppress("DEPRECATION")
    private inline fun <reified T : Parcelable> getParcelableExtraCompat(
        intent: Intent,
        name: String
    ): T? {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra(name, T::class.java)
        } else {
            intent.getParcelableExtra(name)
        }
    }

    @Suppress("DEPRECATION")
    private inline fun <reified T : Parcelable> getParcelableArrayListExtraCompat(
        intent: Intent,
        name: String
    ): ArrayList<T>? {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableArrayListExtra(name, T::class.java)
        } else {
            intent.getParcelableArrayListExtra(name)
        }
    }

    private fun extractDisplayPath(uri: Uri): String {
        val path = uri.lastPathSegment ?: uri.toString()
        return path.replace("primary:", "Internal/").replace(":", "/")
    }
}
