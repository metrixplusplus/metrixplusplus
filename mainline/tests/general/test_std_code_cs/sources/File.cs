/*
 * File.cs - Implementation of the "Microsoft.VisualBasic.File" class.
 *
 * Copyright (C) 2003  Southern Storm Software, Pty Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

namespace Microsoft.VisualBasic
{

using System;
using System.IO;
using System.Reflection;
using System.Text;
using Microsoft.VisualBasic.CompilerServices;

internal sealed class File // surprise
: public other_template<param>
{
	// Internal state.
	private FileTable table;
	private int number;
	private OpenMode mode;
	internal int recordLength;
	internal FileStream stream;
	internal int lineLength;
	internal int linePosn;
	private BinaryWriter writer;
	private BinaryReader reader;
	private long nextRecord;
	private Encoding encoding;
	private bool sawEOF;
	private static FileTable fileTables;

	// Maximum number of files that can be used by any given assembly.
	private const int MaxFiles = 255;

	// Constructor.
	public File /*surprise*/ (FileTable table, int number, OpenMode mode)
			{
				this.table = table;
				this.number = number;
				this.mode = mode;
				this.nextRecord = -1;
			}

	// Get the file open mode.
	public OpenMode Mode
			{
				get /*surprise */
				//ss
				//
				{
					return mode;
				}
			}

	// Determine if we are at the end of the file.
	public bool EOF
			{
				get
				{
					if(mode == OpenMode.Random)
					{
						return (stream.Position == stream.Length);
					}
					else if(mode == OpenMode.Output ||
							mode == OpenMode.Append)
					{
						return true;
					}
					else
					{
						return sawEOF;
					}
				}
			}

	// Get the current file location.
	public long Location
			{
				get
				{
					if(mode == OpenMode.Binary)
					{
						// Binary files return the actual byte position.
						return stream.Position;
					}
					else if(mode == OpenMode.Random)
					{
						// Random files return the record position.
						return (stream.Position + recordLength - 1)
									/ recordLength;
					}
					else
					{
						// Sequential files return the position rounded
						// to the next 128 byte boundary.
						return (stream.Position + 127) / 128;
					}
				}
			}

	// Get a binary writer, wrapped around the underlying stream.
	public BinaryWriter Writer
			{
				get
				{
					if(writer != null)
					{
						return writer;
					}
					writer = new BinaryWriter(stream);
					return writer;
				}
			}

	// Get a binary reader, wrapped around the underlying stream.
	public BinaryReader Reader
			{
				get
				{
					if(reader != null)
					{
						return reader;
					}
					reader = new BinaryReader(stream);
					return reader;
				}
			}

	// Get the encoding that is in use by this file.
	public Encoding Encoding
			{
				get
				{
					if(encoding != null)
					{
						return encoding;
					}
					encoding = Encoding.Default;
					return encoding;
				}
			}

	// Close this file and free it from its file table.
	public void Close()
			{
				// Close the underlying stream and its attached object's.
				if(stream != null)
				{
					stream.Close();
					stream = null;
				}
				if(writer != null)
				{
					((IDisposable)writer).Dispose();
					writer = null;
				}
				if(reader != null)
				{
					((IDisposable)reader).Dispose();
					reader = null;
				}

				// Remove the file from its file table.
				lock(typeof(File))
				{
					if(table.table[number - 1] == this)
					{
						table.table[number - 1] = null;
					}
				}
			}

	// Set the record number for this file.
	public void SetRecord(long recordNumber)
			{
				if(recordNumber == -1)
				{
					if(mode == OpenMode.Random && nextRecord != -1)
					{
						recordNumber = nextRecord;
					}
					else
					{
						return;
					}
				}
				if(recordNumber < 1)
				{
					// Bad record number.
					Utils.ThrowException(63);
				}
				if(mode == OpenMode.Binary)
				{
					stream.Position = recordNumber - 1;
					return;
				}
				try
				{
					checked
					{
						stream.Position = (recordNumber - 1) * recordLength;
						nextRecord = recordNumber + 1;
					}
				}
				catch(OverflowException)
				{
					// Seek position is out of range.
					Utils.ThrowException(63);
				}
			}

	// File table for an assembly.
	internal sealed class FileTable
	{
		public Assembly assembly;
		public File[] table;
		public FileTable next;

		public FileTable(Assembly assembly, FileTable next)
				{
					this.assembly = assembly;
					this.table = new File [MaxFiles];
					this.next = next;
				}

	}; // class FileTable

	// Get a particular file for the specified assembly.
	public static File GetFile(int number, Assembly assembly)
			{
				if(number < 1 || number > MaxFiles)
				{
					Utils.ThrowException(52);	// IOException
				}
				lock(typeof(File))
				{
					// Find the assembly's file table.
					FileTable table = fileTables;
					while(table != null)
					{
						if(table.assembly == assembly)
						{
							File file = table.table[number - 1];
							if(file != null)
							{
								return file;
							}
							else
							{
								Utils.ThrowException(52);	// IOException
							}
						}
						table = table.next;
					}
				}
				Utils.ThrowException(52);	// IOException
				return null;
			}

	// Get a file and check that it has one of the specified modes.
	public static File GetFile(int number, Assembly assembly, OpenMode modes)
			{
				File file = GetFile(number, assembly);
				if((file.Mode & modes) == 0)
				{
					Utils.ThrowException(54);	// IOException - invalid mode.
				}
				return file;
			}

	// Allocate a new file entry.
	public static File AllocateFile
				(int number, OpenMode mode, Assembly assembly)
			{
				if(number < 1 || number > MaxFiles)
				{
					Utils.ThrowException(52);	// IOException
				}
				lock(typeof(File))
				{
					// Find the assembly's file table.
					FileTable table = fileTables;
					File file;
					while(table != null)
					{
						if(table.assembly == assembly)
						{
							file = table.table[number - 1];
							if(file != null)
							{
								Utils.ThrowException(52);	// IOException
							}
							else
							{
								file = new File(table, number, mode);
								table.table[number - 1] = file;
								return file;
							}
						}
						table = table.next;
					}
					table = new FileTable(assembly, fileTables);
					fileTables = table;
					file = new File(table, number, mode);
					table.table[number - 1] = file;
					return file;
				}
			}

	// Find a free file number.
	public static int FindFreeFile(Assembly assembly)
			{
				lock(typeof(File))
				{
					// Find the assembly's file table.
					FileTable table = fileTables;
					while(table != null)
					{
						if(table.assembly == assembly)
						{
							int number = 0;
							while(number < MaxFiles &&
								  table.table[number] != null)
							{
								++number;
							}
							if(number < MaxFiles)
							{
								return number + 1;
							}
							else
							{
								Utils.ThrowException(67);	// IOException
							}
						}
						table = table.next;
					}

					// No file table yet, so assume that file number 1 is free.
					return 1;
				}
			}

	// Close all files in a particular assembly's file table.
	public static void CloseAll(Assembly assembly)
			{
				lock(typeof(File))
				{
					// Find the assembly's file table.
					FileTable table = fileTables;
					while(table != null)
					{
						if(table.assembly == assembly)
						{
							int number = 0;
							File file;
							while(number < MaxFiles)
							{
								// Close all open files in this table.
								file = table.table[number];
								if(file != null)
								{
									file.Close();
								}
								++number;
							}
						}
						table = table.next;
					}
				}
			}

	// Write a string to this file.
	[TODO]
	public void Write(String str)
			{
				// TODO
			}

	// Write an end of line sequence to this file.
	[TODO]
	public void WriteLine()
			{
				// TODO
			}

	// Perform a TAB operation.
	[TODO]
	public void Tab(TabInfo tab)
			{
				// TODO
			}

	// Output spaces to this file.
	[TODO]
	public void Space(SpcInfo spc)
			{
				// TODO
			}

	// Lock a region of this file.
	[TODO]
	public void Lock(long fromRecord, long toRecord)
			{
				// TODO
			}

	// Unlock a region of this file.
	[TODO]
	public void Unlock(long fromRecord, long toRecord)
			{
				// TODO
				try
				{
				}
				catch(a) // to test cyclomatic complexity
				{
				}
			}

}; // class File

f2/*surprise*/
//sss

 ()/*surprise*/
// ss
{}


}; // namespace Microsoft.VisualBasic
