
namespace {
/*!
       *  Finds the optimal cycle ratio of the policy graph
       */
      float_t policy_mcr()
      {
        std::fill(m_col_bfs.begin(), m_col_bfs.end(), my_white);
        color_map_t vcm_ = color_map_t(m_col_bfs.begin(), m_vim);
        typename graph_traits<Graph>::vertex_iterator uv_itr, vie;
        boost::tie(uv_itr, vie) = vertices(m_g);
        float_t mcr = m_bound;
        while ( (uv_itr = std::find_if(uv_itr, vie,
                                       boost::bind(std::equal_to<my_color_type>(),
                                                   my_white,
                                                   boost::bind(&color_map_t::operator[], vcm_, _1)
                                                   )
                                       )
                 ) != vie )
          ///While there are undiscovered vertices
          {
            vertex_t gv = find_cycle_vertex(*uv_itr);
            float_t cr = cycle_ratio(gv) ;
            mcr_bfv(gv, cr, vcm_);
            if ( m_cmp(mcr, cr) )  mcr = cr;
            ++uv_itr;
          }
        return mcr;
      }

      function_after(){}
}


class ALL_operators {
	operator int () {}
	operator new () {}
	operator delete () {}
	operator new[ ] () {}
	operator delete [] () {}
	operator+ () {}
	operator - () {}
	operator * () {}
	operator / () {}
	operator= () {}
	operator< () {}
	operator > () {}
	operator+= () {}
	operator -= () {}
	operator*= () {}
	operator/= () {}
	operator<<() {}
	operator >> () {}
	operator <<=() {}
	operator>>=() {}
	operator==() {}
	operator!=() {}
	operator<=() {}
	operator >= () {}
	operator ++ () {}
	operator--() {}
	operator%() {}
	operator &() {}
	operator ^() {}
	operator !() {}
	operator|() {}
	operator~() {}
	operator &=() {}
	operator ^=() {}
	operator |=() {}
	operator &&() {}
	operator ||  () {}
	operator %=() {}
	operator []  () {}
	operator  ()  () {}
	operator() () {}
	operator()(){}
	operator()   (){}
	operator ()() {}
	operator ()(){}
	operator ,() {}
	operator ->*() {}
	operator->() {}
	operator.() {}
};
