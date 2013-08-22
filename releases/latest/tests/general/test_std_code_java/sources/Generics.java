package edu.stanford.nlp.util;

import java.lang.ref.WeakReference;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Map;
import java.util.SortedSet;
import java.util.Stack;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.WeakHashMap;
import java.util.concurrent.ConcurrentHashMap;

import edu.stanford.nlp.util.concurrent.SynchronizedInterner;

/**
 * A collection of utilities to make dealing with Java generics less
 * painful and verbose.  For example, rather than declaring
 * 
 * <pre>
 * {@code Map<String, List<Pair<IndexedWord, GrammaticalRelation>>> = new HashMap<String, List<Pair<IndexedWord, GrammaticalRelation>>>()}
 * </pre>
 * 
 * you just call <code>Generics.newHashMap()</code>:
 * 
 * <pre>
 * {@code Map<String, List<Pair<IndexedWord, GrammaticalRelation>>> = Generics.newHashMap()}
 * </pre>
 *
 * Java type-inference will almost always just <em>do the right thing</em>
 * (every once in a while, the compiler will get confused before you do,
 * so you might still occasionally have to specify the appropriate types).
 * 
 * This class is based on the examples in Brian Goetz's article
 * <a href="http://www.ibm.com/developerworks/library/j-jtp02216.html">Java
 * theory and practice: The pseudo-typedef antipattern</a>. 
 *
 * @author Ilya Sherman
 */
public class Generics {

  /* Collections */
  public static <E> ArrayList<E> newArrayList() {
    return new ArrayList<E>();
  }
  
  public static <E> ArrayList<E> newArrayList(int size) {
    return new ArrayList<E>(size);
  }
  
  public static <E> ArrayList<E> newArrayList(Collection<? extends E> c) {
    return new ArrayList<E>(c);
  }
  
  public static <E> LinkedList<E> newLinkedList() {
    return new LinkedList<E>();
  }
  
  public static <E> LinkedList<E> newLinkedList(Collection<? extends E> c) {
    return new LinkedList<E>(c);
  }

  public static <E> HashSet<E> newHashSet() {
    return new HashSet<E>();
  }

  public static <E> HashSet<E> newHashSet(int initialCapacity) {
    return new HashSet<E>(initialCapacity);
  }
  
  public static <E> HashSet<E> newHashSet(Collection<? extends E> c) {
    return new HashSet<E>(c);
  }
  
  public static <E> TreeSet<E> newTreeSet() {
    return new TreeSet<E>();
  }
  
  public static <E> TreeSet<E> newTreeSet(Comparator<? super E> comparator) {
    return new TreeSet<E>(comparator);
  }
  
  public static <E> TreeSet<E> newTreeSet(SortedSet<E> s) {
    return new TreeSet<E>(s);
  }
  
  public static <E> Stack<E> newStack() {
    return new Stack<E>();
  }
  
  public static <E> BinaryHeapPriorityQueue<E> newBinaryHeapPriorityQueue() {
    return new BinaryHeapPriorityQueue<E>();
  }

  
  /* Maps */
  public static <K,V> HashMap<K,V> newHashMap() {
    return new HashMap<K,V>();
  }
  
  public static <K,V> HashMap<K,V> newHashMap(int initialCapacity) {
    return new HashMap<K,V>(initialCapacity);
  }
  
  public static <K,V> HashMap<K,V> newHashMap(Map<? extends K,? extends V> m) {
    return new HashMap<K,V>(m);
  }
  
  public static <K,V> WeakHashMap<K,V> newWeakHashMap() {
    return new WeakHashMap<K,V>();
  }
  
  public static <K,V> ConcurrentHashMap<K,V> newConcurrentHashMap() {
    return new ConcurrentHashMap<K,V>();
  }
  
  public static <K,V> ConcurrentHashMap<K,V> newConcurrentHashMap(int initialCapacity) {
    return new ConcurrentHashMap<K,V>(initialCapacity);
  }
  
  public static <K,V> ConcurrentHashMap<K,V> newConcurrentHashMap(int initialCapacity,
      float loadFactor, int concurrencyLevel) {
    return new ConcurrentHashMap<K,V>(initialCapacity, loadFactor, concurrencyLevel);
  }
  
  public static <K,V> TreeMap<K,V> newTreeMap() {
    return new TreeMap<K,V>();
  }
  
  public static <E> Index<E> newIndex() {
    return new Index<E>();
  }
  
  
  /* Other */
  public static <T1,T2> Pair<T1,T2> newPair(T1 first, T2 second) {
    return new Pair<T1,T2>(first, second);
  }

  public static <T1,T2, T3> Triple<T1,T2, T3> newTriple(T1 first, T2 second, T3 third) {
    return new Triple<T1,T2, T3>(first, second, third);
  }

  public static <T> Interner<T> newInterner() {
    return new Interner<T>();
  }
  
  public static <T> SynchronizedInterner<T> newSynchronizedInterner(Interner<T> interner) {
    return new SynchronizedInterner<T>(interner);
  }
  
  public static <T> SynchronizedInterner<T> newSynchronizedInterner(Interner<T> interner,
                                                                    Object mutex) {
    return new SynchronizedInterner<T>(interner, mutex);
  }
  
  public static <T> WeakReference<T> newWeakReference(T referent) {
    return new WeakReference<T>(referent);
  }
}


/*
 * DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
 *
 * Copyright 1997-2009 Sun Microsystems, Inc. All rights reserved.
 *
 * The contents of this file are subject to the terms of either the GNU
 * General Public License Version 2 only ("GPL") or the Common
 * Development and Distribution License("CDDL") (collectively, the
 * "License"). You may not use this file except in compliance with the
 * License. You can obtain a copy of the License at
 * http://www.netbeans.org/cddl-gplv2.html
 * or nbbuild/licenses/CDDL-GPL-2-CP. See the License for the
 * specific language governing permissions and limitations under the
 * License.  When distributing the software, include this License Header
 * Notice in each file and include the License file at
 * nbbuild/licenses/CDDL-GPL-2-CP.  Sun designates this
 * particular file as subject to the "Classpath" exception as provided
 * by Sun in the GPL Version 2 section of the License file that
 * accompanied this code. If applicable, add the following below the
 * License Header, with the fields enclosed by brackets [] replaced by
 * your own identifying information:
 * "Portions Copyrighted [year] [name of copyright owner]"
 *
 * Contributor(s):
 *
 * The Original Software is NetBeans. The Initial Developer of the Original
 * Software is Sun Microsystems, Inc. Portions Copyright 1997-2006 Sun
 * Microsystems, Inc. All Rights Reserved.
 *
 * If you wish your version of this file to be governed by only the CDDL
 * or only the GPL Version 2, indicate your decision by adding
 * "[Contributor] elects to include this software in this distribution
 * under the [CDDL or GPL Version 2] license." If you do not indicate a
 * single choice of license, a recipient has the option to distribute
 * your version of this file under either the CDDL, the GPL Version 2 or
 * to extend the choice of license to its licensees as provided above.
 * However, if you add GPL Version 2 code and therefore, elected the GPL
 * Version 2 license, then the option applies only if the new code is
 * made subject to such option by the copyright holder.
 */
package org.netbeans.test.codegen;

import java.util.Collection;
import java.util.List;

/**
 *
 * @author Martin Matula
 */
public class Generics<T extends Collection> extends java.util.AbstractList<T> implements List<T> {
    private final List<T> inner;

    /** Creates a new instance of Generics */
    public Generics(List<T> innerList) {
        inner = innerList;
    }

    public T get(int index) {
        return inner.get(index);
    }

    public int size() {
        return inner.size();
    }
}
