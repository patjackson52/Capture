package com.capture.app.data

import android.content.Context
import android.net.Uri
import androidx.documentfile.provider.DocumentFile
import com.capture.app.model.Attachment
import com.capture.app.model.CaptureData
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.withContext
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

class CaptureRepository(private val context: Context) {

    private val prefs = PreferencesManager(context)

    companion object {
        private val FILE_TIMESTAMP_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd_HHmmss")
        private val YAML_TIMESTAMP_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss")
    }

    /**
     * Saves a capture to the user-selected folder.
     * Returns true on success, error message on failure.
     */
    suspend fun save(capture: CaptureData): Result<String> = withContext(Dispatchers.IO) {
        try {
            val locationUri = prefs.saveLocationUri.first()
                ?: return@withContext Result.failure(Exception("No save location set. Tap the folder path to choose one."))

            val treeUri = Uri.parse(locationUri)
            val rootDir = DocumentFile.fromTreeUri(context, treeUri)
                ?: return@withContext Result.failure(Exception("Cannot access save folder. It may have been moved or deleted."))

            if (!rootDir.canWrite()) {
                return@withContext Result.failure(Exception("Cannot write to save folder. Please choose a new location."))
            }

            val now = LocalDateTime.now()
            val timestamp = now.format(FILE_TIMESTAMP_FORMAT)
            val yamlTimestamp = now.format(YAML_TIMESTAMP_FORMAT)
            val savedFiles = mutableListOf<String>()

            // Save attachments first
            for (attachment in capture.attachments) {
                val ext = extensionForMimeType(attachment.mimeType)
                val fileName = "${timestamp}_${attachment.displayName ?: "file"}.$ext"
                val mimeType = attachment.mimeType ?: "application/octet-stream"

                val newFile = rootDir.createFile(mimeType, fileName)
                    ?: continue

                context.contentResolver.openInputStream(attachment.uri)?.use { input ->
                    context.contentResolver.openOutputStream(newFile.uri)?.use { output ->
                        input.copyTo(output)
                    }
                }
                savedFiles.add(fileName)
            }

            // Save text note (always, even if empty — serves as metadata sidecar for attachments)
            if (capture.text.isNotBlank() || capture.attachments.isNotEmpty()) {
                val noteFileName = "${timestamp}_note.md"
                val noteFile = rootDir.createFile("text/markdown", noteFileName)
                    ?: return@withContext Result.failure(Exception("Failed to create note file."))

                val content = buildNoteContent(capture, yamlTimestamp, savedFiles)
                context.contentResolver.openOutputStream(noteFile.uri)?.use { output ->
                    output.write(content.toByteArray(Charsets.UTF_8))
                }
                savedFiles.add(noteFileName)
            }

            // Persist any new tags
            if (capture.tags.isNotEmpty()) {
                prefs.addTags(capture.tags.toSet())
            }

            val fileWord = if (savedFiles.size == 1) "file" else "files"
            Result.success("Saved ${savedFiles.size} $fileWord")
        } catch (e: Exception) {
            Result.failure(Exception("Save failed: ${e.message}"))
        }
    }

    private fun buildNoteContent(
        capture: CaptureData,
        yamlTimestamp: String,
        attachmentFileNames: List<String>
    ): String = buildString {
        // YAML front matter
        appendLine("---")
        if (capture.tags.isNotEmpty()) {
            appendLine("tags: [${capture.tags.joinToString(", ")}]")
        }
        appendLine("source: ${capture.source.label}")
        appendLine("captured: $yamlTimestamp")
        if (attachmentFileNames.isNotEmpty()) {
            appendLine("attachments:")
            for (name in attachmentFileNames) {
                if (!name.endsWith("_note.md")) {
                    appendLine("  - $name")
                }
            }
        }
        appendLine("---")
        appendLine()

        // Body
        if (capture.text.isNotBlank()) {
            appendLine(capture.text)
            appendLine()
        }

        // Embed attachments with Obsidian-style wikilinks
        for (name in attachmentFileNames) {
            if (!name.endsWith("_note.md")) {
                appendLine("![[${name}]]")
            }
        }
    }

    private fun extensionForMimeType(mimeType: String?): String = when {
        mimeType == null -> "bin"
        mimeType.startsWith("image/png") -> "png"
        mimeType.startsWith("image/jpeg") || mimeType.startsWith("image/jpg") -> "jpg"
        mimeType.startsWith("image/webp") -> "webp"
        mimeType.startsWith("image/gif") -> "gif"
        mimeType.startsWith("image/") -> "img"
        mimeType == "application/pdf" -> "pdf"
        mimeType.contains("text/plain") -> "txt"
        mimeType.contains("text/html") -> "html"
        else -> "bin"
    }
}
