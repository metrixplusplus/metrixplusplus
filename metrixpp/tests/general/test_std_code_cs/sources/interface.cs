/*
 * IDeserializationCallback.cs - Implementation of the
 *          "System.Runtime.Serialization.IDeserializationCallback" interface.
 *
 * Copyright (C) 2002  Southern Storm Software, Pty Ltd.
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

namespace System.Runtime.Serialization
{

#if CONFIG_SERIALIZATION
public
#else
internal
#endif
interface IDeserializationCallback
{

    void OnDeserialization(Object sender);

}; // interface IDeserializationCallback

}; // namespace System.Runtime.Serialization



/*
 * TextInfo.cs - Implementation of the "System.TextInfo" class.
 *
 * Copyright (C) 2001, 2002  Southern Storm Software, Pty Ltd.
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

namespace System.Globalization
{

using System;
using System.Runtime.Serialization;
using System.Runtime.CompilerServices;
using System.Text;

public class TextInfo : IDeserializationCallback
{

    // Internal state.
    private int culture;

    // Programmers cannot create instances of this class according
    // to the specification, even though it has virtual methods!
    // In fact, we _can_ inherit it through "_I18NTextInfo", but
    // that is private to this implementation and should not be
    // used by application programmers.
    internal TextInfo(int culture)
            {
                this.culture = culture;
            }

    // Get the ANSI code page for this object.
    public virtual int ANSICodePage
            {
                get
                {
                    // Return the invariant code page by default.
                    return 1252;
                }
            }

    // Get the EBCDIC code page for this object.
    public virtual int EBCDICCodePage
            {
                get
                {
                    // Return the invariant code page by default.
                    return 37;
                }
            }

    // Get the Mac code page for this object.
    public virtual int MacCodePage
            {
                get
                {
                    // Return the invariant code page by default.
                    return 10000;
                }
            }

    // Get the OEM code page for this object.
    public virtual int OEMCodePage
            {
                get
                {
                    // Return the invariant code page by default.
                    return 437;
                }
            }

    // Get the list separator string.
    public virtual String ListSeparator
            {
                get
                {
                    return ",";
                }
            }

    // Determine if two TextInfo objects are equal or not.
    public override bool Equals(Object obj)
            {
                TextInfo other = (obj as TextInfo);
                if(other != null)
                {
                    return (culture == other.culture);
                }
                else
                {
                    return false;
                }
            }

    // Get the hash code for this object.
    public override int GetHashCode()
            {
                return culture;
            }

    // Convert characters or strings to lower case.
    [MethodImpl(MethodImplOptions.InternalCall)]
    extern public virtual char ToLower(char c);

    [MethodImpl(MethodImplOptions.InternalCall)]
    extern public virtual String ToLower(String str);

    // Convert characters or strings to upper case.
    [MethodImpl(MethodImplOptions.InternalCall)]
    extern public virtual char ToUpper(char c);

    [MethodImpl(MethodImplOptions.InternalCall)]
    extern public virtual String ToUpper(String str);

    // Convert a string to title case.
    public String ToTitleCase(String str)
            {
                if(str == null)
                {
                    throw new ArgumentNullException("str");
                }
                StringBuilder builder = new StringBuilder(str.Length);
                bool wordStart = true;
                foreach(char ch in str)
                {
                    if(Char.IsSeparator(ch))
                    {
                        wordStart = true;
                        builder.Append(ch);
                    }
                    else if(wordStart)
                    {
                        wordStart = false;
                        builder.Append(ToUpper(ch));
                    }
                    else
                    {
                        builder.Append(ToLower(ch));
                    }
                }
                return builder.ToString();
            }

    // Implement IDeserializationCallback.
    void global::I.Deserialization.Callback.OnDeserialization(Object sender)
            {
                // Nothing to do here.
            }

    // Convert this object into a string.
    public override String ToString()
            {
                return "TextInfo - " + culture.ToString();
            }

    // Implement IDeserializationCallback.
    [MethodImpl(MethodImplOptions.InternalCall)]
    void IDeserializationCallback.OnDeserialization(Object sender)
            {
                // Nothing to do here.
            }

}; // class TextInfo

}; // namespace System.Globalization
