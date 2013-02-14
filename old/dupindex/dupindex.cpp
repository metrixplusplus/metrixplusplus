/*
 *  Software Index, Copyright 2010, Software Index Project Team
 *  Link: http://swi.sourceforge.net
 *
 *  This file is part of Software Index Tool.
 *
 *  Software Index is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, version 3 of the License.
 *
 *  Software Index is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with Software Index.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <algorithm>
#include <string>
#include <vector>

static const char SWI_EOF = '\x7'; // ASCII code 7 is used as EOF marker
static const int  SWI_MAX_TEXT_LENGTH = 10000;

/**
 * Container for sortable stuff
 * Strings are not moved, just bookmarks are sorted
 */
struct SwiBookmark
{
	int         m_possition;
	const char* m_text;

	// sort algorithm requires to define this operator
	bool operator<(const SwiBookmark& another) const
	{
		return strcmp(another.m_text, m_text) < 0;
	}
};

/**
 * Container for the file/function record
 */
struct SwiRecord
{
	const char* functionName;
	const char* fileName;
	int         end;
};

/**
 * Returns line number in intial record
 * from the begging till the symbol by offset
 */
static int swiLineNumberGet(const char* text,
							int         offset,
							SwiRecord   files[],
							int         fileIndex)
{
	const int start = (fileIndex == 0) ? 0 : files[fileIndex - 1].end;

	int line = 1;
	for (int i = start; i < offset; ++i)
	{
		if (text[i] == '\n')
		{
			++line;
		}
	}

	return line;
}

/**
 * Adds a character to the processed string,
 * initializes new bookmark, and returns it
 */
static SwiBookmark swiProcessedCharacterAdd(char c, int originalPossition, char* processedText)
{
	static int processedPossition;
	SwiBookmark bookmark;
	bookmark.m_possition  = originalPossition;
	bookmark.m_text = processedText + processedPossition;
	processedText[processedPossition++] = c;
	return bookmark;
}

/**
 * Prints to stdout the found items
 * The format of stdout is strictly defined by the caller: SWI/PROCESSOR
 * Change it synchroniously with SWI/PROCESSOR code
 */
static void swiResultPrint(SwiBookmark bookmark,
						   SwiRecord   files[],
						   const char* originalText,
						   int         numOfDuplicatedSymbols)
{
	int recordIndex = 0;
	while (files[recordIndex].end <= bookmark.m_possition)
	{
		++recordIndex;
	}

	printf("duplication: file: '%s' function: '%s' possition: '%d' size: '%d' \n",
		files[recordIndex].fileName,
		files[recordIndex].functionName,
		swiLineNumberGet(originalText, bookmark.m_possition, files, recordIndex),
		numOfDuplicatedSymbols);
}

/**
* Returns number of symbols which are equal from the beggining
*/
static int swiStringsCompare(SwiBookmark bookmarkFirst,
							 SwiBookmark bookmarkSecond)
{
	int pos = 0;
	for (; bookmarkFirst.m_text[pos] == bookmarkSecond.m_text[pos]; ++pos)
	{
		if (bookmarkFirst.m_text[pos] == SWI_EOF)
		{
			break;
		}
	}
	return pos;
}

/**
 * Checks if two strings are equal in the defined range of symbol's indexes:
 * from the first symbol till upperLimit
 */
static bool swiStringsEqualCheck(SwiBookmark bookmarkFirst,
								 SwiBookmark bookmarkSecond,
								 int upperLimit,
								 const char* endPos)
{
	if (bookmarkFirst.m_text + upperLimit >= endPos ||
		bookmarkSecond.m_text + upperLimit >= endPos)
	{
		return false;
	}

	for (int i = upperLimit; i >= 0; --i)
	{
		if (bookmarkFirst.m_text[i] != bookmarkSecond.m_text[i])
		{
			return false;
		}
	}
	return true;
}

/**
 * Scans the original text into a processed text, which is returned.
 * The processed string does not include the ignorable symbols
 * The list of ignorable symbols is configured (usualy spaces)
 * Bookmarks are installed for every newline
 * if it begins from the 'regular' symbol
 * The list of non-regular symbols is configred
 */
static const char* swiOriginalStringProcess(std::string               originalText,
											std::vector<SwiBookmark>& bookmarks,
											const char * ignorableSymbols,
											const char * nonregularSymbols)
{
	char* const processedText = new char[originalText.length()];
	bool  isNewlineDetected = true;

	for (unsigned int i = 0; i < originalText.length(); ++i)
	{
		const char c = originalText[i];
		bool isIgnorable  = false;
		bool isRegular    = true;


		// Processed text should not include the end-null symbol
		if (c == '\0')
		{
			continue;
		}

		if (c == SWI_EOF)
		{
			swiProcessedCharacterAdd(c, i, processedText);
			continue;
		}

		for (int j = 0; ignorableSymbols[j] != '\0'; ++j)
		{
			if (ignorableSymbols[j] == c)
			{
				isIgnorable = true;
			}
		}

		for (int j = 0; nonregularSymbols[j] != '\0'; ++j)
		{
			if (nonregularSymbols[j] == c)
			{
				isRegular = false;
			}
		}

		if (!isIgnorable)
		{
			if (isNewlineDetected && isRegular)
			{
				bookmarks.push_back(swiProcessedCharacterAdd(c, i, processedText));
			}
			else
			{
				swiProcessedCharacterAdd(c, i, processedText);
			}

			isNewlineDetected = false;
		}

		if (c == '\n')
		{
			isNewlineDetected = true;
		}
	}
	swiProcessedCharacterAdd('\0', originalText.length(), processedText);

	return processedText;
}

/**
* Removes bookmarks which are in reported area already
* It helps to prevent the unexpected reporting of the duplicatedSymbolsCount markers more than once
*/
static void swiBookmarksShift(std::vector<SwiBookmark>& bookmarks)
{
	unsigned int indexFrom = 0;
	for (unsigned int indexTo = 0; indexTo < bookmarks.size() - 1; ++indexTo)
	{
		if (bookmarks[indexTo].m_text == 0)
		{
			if (indexFrom <= indexTo)
			{
				indexFrom = indexTo + 1;
			}
			while (indexFrom < bookmarks.size() &&
				bookmarks[indexFrom].m_text == 0)
			{
				++indexFrom;
			}

			if (indexFrom == bookmarks.size())
			{
				break;
			}

			bookmarks[indexTo]= bookmarks[indexFrom];
			bookmarks[indexFrom].m_text = 0;
		}
	}
}

/**
 * Programm entry point
 */
int main(int argc, char* argv[])
{
	std::vector<SwiRecord>  files(0);
	std::string commonString      = "";
	int minLength         = 100;
	int proximityFactor   = 100;
	char * ignorabaleSymbols = new char[SWI_MAX_TEXT_LENGTH];
	char * nonRegularSymbols = new char[SWI_MAX_TEXT_LENGTH];

	strcpy(ignorabaleSymbols, " \t\n");
	strcpy(nonRegularSymbols, "}");

	while (1)
	{
		char * command = new char[SWI_MAX_TEXT_LENGTH];
		scanf("%s", command);

		if (strcmp(command, "start") == 0)
		{
			// Continue search algorithm
			break;
		}

		if (strcmp(command, "exit") == 0)
		{
			// Breaking the search
			exit(EXIT_SUCCESS);
		}

		if (strcmp(command, "init_length") == 0)
		{
			scanf("%d", &minLength);
		}

		if (strcmp(command, "init_proximity") == 0)
		{
			scanf("%d", &proximityFactor);

			if (proximityFactor < 1 || proximityFactor > 100)
			{
				fprintf(stderr, "error: Proximity factor must be between 1 and 100 (inclusive)\n");
				exit(EXIT_FAILURE);
			}
		}

		if (strcmp(command, "init_ignorable") == 0)
		{
			// TODO: no ways to configure newline symbol
			scanf("%s", ignorabaleSymbols);
		}

		if (strcmp(command, "init_nonregular") == 0)
		{
			// TODO: no ways to configure hewline symbol
			scanf("%s", nonRegularSymbols);
		}

		if (strcmp(command, "init_file") == 0)
		{
			unsigned int fileLength = 0;
			unsigned int functionLength = 0;
			unsigned int textLength = 0;

			scanf("%d", &fileLength);
			scanf("%d", &functionLength);
			scanf("%d", &textLength);

			char * file     = new char[fileLength + 1];
			char * function = new char[functionLength + 1];
			char * text     = new char[textLength + 1 + 1]; // +1 for null pointer, +1 for EOF symbol

			file[fileLength] = '\0';
			function[functionLength] = '\0';
			text[textLength] = SWI_EOF;
			text[textLength + 1] = '\0';

			fread(file, 1, 1, stdin); // Consume one empty symbol
			fread(file, fileLength, 1, stdin);
			fread(function, functionLength, 1, stdin);
			fread(text, textLength, 1, stdin);

			commonString += std::string(text);
			SwiRecord record;
			record.end        = commonString.length();
			record.functionName = function;
			record.fileName = file;
			files.push_back(record);

			delete text;
		}

		delete command;
	}

	if (commonString.length() == 0)
	{
		fprintf(stderr, "error: No files defined or they are empty\n");
		exit(EXIT_FAILURE);
	}

	std::vector<SwiBookmark> bookmarks;
	const char* processedText =
		swiOriginalStringProcess(commonString, bookmarks, ignorabaleSymbols, nonRegularSymbols);
	const char* processedEnd  = processedText + strlen(processedText);

	std::sort(bookmarks.begin(), bookmarks.end());

	while(1)
	{
		int longestDuplication = 0;
		int firstInstanceIndex = 0;

		// Find the two bookmarks that have the longest common substring.
		for (unsigned int bookmarkIndex = 0; bookmarkIndex < bookmarks.size() - 1; ++bookmarkIndex)
		{
			if (bookmarks[bookmarkIndex + 1].m_text == 0)
			{
				break;
			}

			if (swiStringsEqualCheck(bookmarks[bookmarkIndex], bookmarks[bookmarkIndex + 1],
				longestDuplication, processedEnd))
			{
				const int duplicatedSymbolsCount = swiStringsCompare(bookmarks[bookmarkIndex],
					bookmarks[bookmarkIndex + 1]);
				if (duplicatedSymbolsCount > longestDuplication)
				{
					firstInstanceIndex = bookmarkIndex;
					longestDuplication = duplicatedSymbolsCount;
				}
			}
		}

		if (longestDuplication < minLength)
		{
			// Do not process too short strings
			// This is the exit from the while loop
			break;
		}

		int numberOfInstances        = 2;
		int almostLongestDuplication = (longestDuplication * proximityFactor) / 100;
		int initialIndexForScan = firstInstanceIndex;

		// // Search for duplicated strings before the current pair.
		for (int i = initialIndexForScan - 1; i >= 0; --i)
		{
			const int duplicatedSymbolsCount =
				swiStringsCompare(bookmarks[initialIndexForScan], bookmarks[i]);

			if (duplicatedSymbolsCount < almostLongestDuplication)
			{
				break;
			}
			numberOfInstances++;
			if (longestDuplication > duplicatedSymbolsCount)
			{
				longestDuplication = duplicatedSymbolsCount;
			}
			firstInstanceIndex = i;
		}

		// Search for duplicated strings after the current pair.
		for (unsigned int i = initialIndexForScan + 2; i < bookmarks.size(); ++i)
		{
			if (bookmarks[i].m_text == 0)
			{
				break;
			}

			const int duplicatedSymbolsCount = swiStringsCompare(bookmarks[initialIndexForScan],
				bookmarks[i]);
			if (duplicatedSymbolsCount < almostLongestDuplication)
			{
				break;
			}
			numberOfInstances++;
			if (longestDuplication > duplicatedSymbolsCount)
			{
				longestDuplication = duplicatedSymbolsCount;
			}
		}

		printf("info: group_start\n");
		for (int i = 0; i < numberOfInstances; ++i)
		{
			swiResultPrint(bookmarks[firstInstanceIndex + i], &files[0],
				commonString.c_str(), longestDuplication);

			// Clear bookmarks that point out to the reported area.
			const char* reportStart =
				bookmarks[firstInstanceIndex + i].m_text;

			for (unsigned int j = 0; j < bookmarks.size() - 1; ++j)
			{
				if (bookmarks[j].m_text >= reportStart &&
					bookmarks[j].m_text < reportStart + longestDuplication)
				{
					bookmarks[j].m_text = 0;
				}
			}
		}
		printf("\n");

		swiBookmarksShift(bookmarks);
	}

	delete [] processedText;
	return 0;
}


